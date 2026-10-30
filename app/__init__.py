import os

from dotenv import load_dotenv
from flask import Flask
from flask_appbuilder import AppBuilder
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import URL

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
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Registrar los modelos del dominio antes de inicializar Flask-AppBuilder.
from app import models  # noqa: E402, F401

with app.app_context():
    appbuilder = AppBuilder(app, db.session)

from datetime import date
from flask import render_template
from sqlalchemy import text


@app.route('/dashboard')
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
