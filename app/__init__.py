import os

from dotenv import load_dotenv
from flask import Flask
from flask_login import login_required
from flask_wtf.csrf import CSRFProtect
import click
from flask_appbuilder import AppBuilder
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import URL
from werkzeug.security import generate_password_hash
from email_validator import validate_email, EmailNotValidError

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '')
if not app.config['SECRET_KEY']:
    raise RuntimeError('Configura SECRET_KEY en el archivo .env')

app.config['SQLALCHEMY_DATABASE_URI'] = URL.create(
    'mysql+pymysql',
    username=os.environ.get('MYSQL_USER', 'root'),
    password=os.environ.get('MYSQL_PASSWORD', ''),
    host=os.environ.get('MYSQL_HOST', '127.0.0.1'),
    port=int(os.environ.get('MYSQL_PORT', '3306')),
    database=os.environ.get('MYSQL_DATABASE', 'dbgastos'),
    query={'charset': 'utf8mb4'},
)
CSRFProtect(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['APP_NAME'] = 'Mis gastos'
app.config['BABEL_DEFAULT_LOCALE'] = 'es'
app.config['AUTH_USER_REGISTRATION'] = False
app.config['FAB_PASSWORD_HASH_METHOD'] = 'pbkdf2:sha256:1000000'
app.config['AUTH_DB_FAKE_PASSWORD_HASH_CHECK'] = generate_password_hash(
    'comprobacion-sin-usuario', method=app.config['FAB_PASSWORD_HASH_METHOD']
)

db = SQLAlchemy(app)

# Registrar los modelos del dominio antes de inicializar Flask-AppBuilder.
from app import models  # noqa: E402, F401
from app.security import EmailSecurityManager
from app.views import InicioView, registrar_vistas

with app.app_context():
    appbuilder = AppBuilder(app, db.session, indexview=InicioView, security_manager_class=EmailSecurityManager)
    registrar_vistas(appbuilder)
    app.login_manager.login_view = 'AuthDBView.login'


@app.cli.command('crear-admin')
@click.option('--correo', prompt='Correo electrónico')
@click.password_option(prompt='Contraseña', confirmation_prompt='Repite la contraseña')
def crear_admin(correo, password):
    """Crear un administrador local usando correo y contraseña."""
    correo = correo.strip().lower()
    try:
        correo = validate_email(correo, check_deliverability=False).normalized.lower()
    except EmailNotValidError as exc:
        raise click.ClickException(f'Correo inválido: {exc}')
    if len(correo) > 64:
        raise click.ClickException('El correo debe tener como máximo 64 caracteres.')
    if not password:
        raise click.ClickException('La contraseña no puede estar vacía.')
    sm = appbuilder.sm
    if sm.find_user(email=correo) or sm.find_user(username=correo):
        raise click.ClickException('Ya existe un usuario con ese correo.')
    if not sm.add_user(correo, 'Administrador', 'Local', correo, sm.find_role('Admin'), password):
        raise click.ClickException('No se pudo crear el administrador.')
    click.echo('Administrador creado correctamente.')

@app.cli.command('cargar-ejemplos')
def cargar_ejemplos_comando():
    """Cargar ejemplos cuando las tablas de gastos estén vacías."""
    from app.ejemplos import cargar_ejemplos
    try:
        cargar_ejemplos()
    except ValueError as exc:
        raise click.ClickException(str(exc))
    click.echo('Datos de ejemplo cargados correctamente.')


from datetime import date
from flask import render_template
from sqlalchemy import text


@app.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    params = {'mes': today.month, 'anio': today.year}
    gastos_mes = db.session.execute(text('''
        SELECT COALESCE(SUM(monto), 0) FROM gastos
        WHERE MONTH(fecha) = :mes AND YEAR(fecha) = :anio
    '''), params).scalar_one()
    presupuesto = db.session.execute(text('''
        SELECT COALESCE(SUM(monto_limite), 0) FROM presupuestos
        WHERE mes = :mes AND anio = :anio
    '''), params).scalar_one()
    cuentas = db.session.execute(text('SELECT COUNT(*) FROM cuentas')).scalar_one()
    recientes = db.session.execute(text('''
        SELECT g.fecha, g.descripcion, g.monto, s.nombre AS subcategoria, c.nombre AS cuenta
        FROM gastos g JOIN subcategorias s ON s.id = g.subcategoria_id
        JOIN cuentas c ON c.id = g.cuenta_id ORDER BY g.fecha DESC, g.id DESC LIMIT 6
    ''')).mappings().all()
    meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
             'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    return render_template('dashboard.html', gastos_mes=gastos_mes, presupuesto=presupuesto,
                           cuentas=cuentas, recientes=recientes,
                           periodo=f'{meses[today.month - 1]} de {today.year}')


@app.route('/reportes')
@login_required
def reportes():
    from flask import abort, request

    hoy = date.today()
    try:
        mes = int(request.args.get('mes', hoy.month))
        anio = int(request.args.get('anio', hoy.year))
    except (TypeError, ValueError):
        abort(400, 'El mes y el año deben ser números.')
    if not 1 <= mes <= 12 or not 1 <= anio <= 9999:
        abort(400, 'El mes o el año no es válido.')
    params = {'mes': mes, 'anio': anio}
    categoria = db.session.execute(text('''
        SELECT c.nombre, SUM(g.monto) AS total FROM gastos g
        JOIN subcategorias s ON s.id = g.subcategoria_id
        JOIN categorias c ON c.id = s.categoria_id
        WHERE MONTH(g.fecha) = :mes AND YEAR(g.fecha) = :anio
        GROUP BY c.id, c.nombre ORDER BY total DESC
    '''), params).mappings().all()
    cuenta = db.session.execute(text('''
        SELECT c.nombre, SUM(g.monto) AS total FROM gastos g
        JOIN cuentas c ON c.id = g.cuenta_id
        WHERE MONTH(g.fecha) = :mes AND YEAR(g.fecha) = :anio
        GROUP BY c.id, c.nombre ORDER BY total DESC
    '''), params).mappings().all()
    presupuesto = db.session.execute(text('''
        SELECT c.nombre, p.monto_limite, COALESCE(t.total, 0) AS total,
               p.monto_limite - COALESCE(t.total, 0) AS restante
        FROM presupuestos p JOIN categorias c ON c.id = p.categoria_id
        LEFT JOIN (
            SELECT s.categoria_id, SUM(g.monto) AS total FROM gastos g
            JOIN subcategorias s ON s.id = g.subcategoria_id
            WHERE MONTH(g.fecha) = :mes AND YEAR(g.fecha) = :anio
            GROUP BY s.categoria_id
        ) t ON t.categoria_id = c.id
        WHERE p.mes = :mes AND p.anio = :anio ORDER BY c.nombre
    '''), params).mappings().all()
    return render_template('reportes.html', mes=mes, anio=anio, categorias=categoria,
                           cuentas=cuenta, presupuestos=presupuesto)


@app.route('/asistente', methods=['GET', 'POST'])
@login_required
def asistente():
    from flask_wtf import FlaskForm
    from wtforms import StringField
    from wtforms.validators import DataRequired, Length
    from app.assistant import sugerir_subcategoria

    class ConsultaForm(FlaskForm):
        descripcion = StringField('Descripción del gasto', validators=[DataRequired(), Length(max=200)])

    form = ConsultaForm()
    sugerencia = None
    consultado = form.validate_on_submit()
    if consultado:
        ejemplos = db.session.execute(text('''
            SELECT s.id, s.nombre, g.descripcion FROM gastos g
            JOIN subcategorias s ON s.id = g.subcategoria_id
            WHERE g.descripcion IS NOT NULL AND g.descripcion <> ''
        ''')).all()
        sugerencia = sugerir_subcategoria(form.descripcion.data, ejemplos)
    return render_template('asistente.html', form=form, consultado=consultado, sugerencia=sugerencia)
