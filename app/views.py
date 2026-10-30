"""Vistas CRUD para las seis tablas del sistema."""

from flask import redirect, url_for
from flask_appbuilder import ModelView, expose
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.views import IndexView
from wtforms.validators import DataRequired, NumberRange

from app.models import Categoria, Subcategoria, Cuenta, Gasto, Presupuesto, GastoRecurrente


class InicioView(IndexView):
    @expose('/')
    def index(self):
        return redirect(url_for('dashboard'))


class CategoriaView(ModelView):
    datamodel = SQLAInterface(Categoria)
    list_columns = ['nombre', 'descripcion']
    add_columns = edit_columns = ['nombre', 'descripcion']
    label_columns = {'nombre': 'Nombre', 'descripcion': 'Descripción'}


class SubcategoriaView(ModelView):
    datamodel = SQLAInterface(Subcategoria)
    list_columns = ['nombre', 'categoria']
    add_columns = edit_columns = ['nombre', 'categoria']
    label_columns = {'nombre': 'Nombre', 'categoria': 'Categoría'}


class CuentaView(ModelView):
    datamodel = SQLAInterface(Cuenta)
    list_columns = add_columns = edit_columns = ['nombre', 'saldo_inicial']
    label_columns = {'nombre': 'Nombre', 'saldo_inicial': 'Saldo inicial'}


class GastoView(ModelView):
    datamodel = SQLAInterface(Gasto)
    list_columns = ['fecha', 'descripcion', 'subcategoria', 'cuenta', 'monto']
    add_columns = edit_columns = ['subcategoria', 'cuenta', 'monto', 'descripcion', 'fecha']
    label_columns = {'fecha': 'Fecha', 'descripcion': 'Descripción', 'subcategoria': 'Subcategoría', 'cuenta': 'Cuenta', 'monto': 'Monto'}
    validators_columns = {'monto': [DataRequired(), NumberRange(min=0.01, message='El monto debe ser mayor que cero.')]}


class PresupuestoView(ModelView):
    datamodel = SQLAInterface(Presupuesto)
    list_columns = add_columns = edit_columns = ['categoria', 'monto_limite', 'mes', 'anio']
    label_columns = {'categoria': 'Categoría', 'monto_limite': 'Monto límite', 'mes': 'Mes', 'anio': 'Año'}
    validators_columns = {
        'monto_limite': [DataRequired(), NumberRange(min=0.01)],
        'mes': [DataRequired(), NumberRange(min=1, max=12)],
        'anio': [DataRequired(), NumberRange(min=1, max=9999)],
    }


class GastoRecurrenteView(ModelView):
    datamodel = SQLAInterface(GastoRecurrente)
    list_columns = add_columns = edit_columns = ['subcategoria', 'cuenta', 'monto', 'frecuencia', 'proxima_fecha']
    label_columns = {'subcategoria': 'Subcategoría', 'cuenta': 'Cuenta', 'monto': 'Monto', 'frecuencia': 'Frecuencia', 'proxima_fecha': 'Próxima fecha'}
    validators_columns = {'monto': [DataRequired(), NumberRange(min=0.01)]}


def registrar_vistas(appbuilder):
    for vista, nombre, icono in [
        (CategoriaView, 'Categorías', 'fa-folder-open'),
        (SubcategoriaView, 'Subcategorías', 'fa-folder'),
        (CuentaView, 'Cuentas', 'fa-university'),
        (GastoView, 'Gastos', 'fa-money'),
        (PresupuestoView, 'Presupuestos', 'fa-pie-chart'),
        (GastoRecurrenteView, 'Gastos recurrentes', 'fa-repeat'),
    ]:
        appbuilder.add_view(vista, nombre, icon=icono, category='Gestionar', category_icon='fa-list')
    appbuilder.add_link('Dashboard', href='/dashboard', icon='fa-home')
    appbuilder.add_link('Reportes', href='/reportes', icon='fa-bar-chart')
    appbuilder.add_link('Asistente', href='/asistente', icon='fa-lightbulb-o')
