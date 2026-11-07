"""Datos de ejemplo para una base de gastos que todavía está vacía."""
from calendar import monthrange
from datetime import date
from decimal import Decimal

from app import db
from app.models import Categoria, Subcategoria, Cuenta, Gasto, Presupuesto, GastoRecurrente


def cargar_ejemplos():
    modelos = (Categoria, Subcategoria, Cuenta, Gasto, Presupuesto, GastoRecurrente)
    if any(db.session.query(modelo.id).first() for modelo in modelos):
        raise ValueError('Los datos de ejemplo solo se cargan cuando las seis tablas están vacías.')

    hoy = date.today()
    fecha = lambda dia: hoy.replace(day=min(dia, hoy.day))
    try:
        alimentacion = Categoria(nombre='Alimentación', descripcion='Compras de alimentos y comidas')
        transporte = Categoria(nombre='Transporte', descripcion='Traslados y movilidad')
        vivienda = Categoria(nombre='Vivienda', descripcion='Alquiler y servicios del hogar')
        salud = Categoria(nombre='Salud', descripcion='Medicamentos y atención médica')
        supermercado = Subcategoria(nombre='Supermercado', categoria=alimentacion)
        restaurantes = Subcategoria(nombre='Restaurantes', categoria=alimentacion)
        transporte_publico = Subcategoria(nombre='Transporte público', categoria=transporte)
        servicios = Subcategoria(nombre='Servicios del hogar', categoria=vivienda)
        farmacia = Subcategoria(nombre='Farmacia', categoria=salud)
        efectivo = Cuenta(nombre='Efectivo', saldo_inicial=Decimal('500.00'))
        banco = Cuenta(nombre='Cuenta bancaria', saldo_inicial=Decimal('2500.00'))
        db.session.add_all([alimentacion, transporte, vivienda, salud, supermercado, restaurantes,
                            transporte_publico, servicios, farmacia, efectivo, banco])
        db.session.add_all([
            Gasto(subcategoria=supermercado, cuenta=banco, monto=Decimal('185.50'), descripcion='Compra de alimentos en supermercado', fecha=fecha(2)),
            Gasto(subcategoria=supermercado, cuenta=efectivo, monto=Decimal('35.00'), descripcion='Compra de pan y leche', fecha=fecha(5)),
            Gasto(subcategoria=restaurantes, cuenta=efectivo, monto=Decimal('42.00'), descripcion='Almuerzo en restaurante', fecha=fecha(8)),
            Gasto(subcategoria=transporte_publico, cuenta=efectivo, monto=Decimal('18.00'), descripcion='Pasajes de transporte público', fecha=fecha(10)),
            Gasto(subcategoria=servicios, cuenta=banco, monto=Decimal('160.00'), descripcion='Pago mensual de internet', fecha=fecha(12)),
            Gasto(subcategoria=farmacia, cuenta=banco, monto=Decimal('68.50'), descripcion='Compra de medicamentos', fecha=fecha(15)),
            Gasto(subcategoria=supermercado, cuenta=banco, monto=Decimal('75.00'), descripcion='Compra de frutas y verduras', fecha=fecha(18)),
            Gasto(subcategoria=transporte_publico, cuenta=efectivo, monto=Decimal('24.00'), descripcion='Pasajes para ir al trabajo', fecha=fecha(20)),
        ])
        for categoria, monto in [(alimentacion, '700.00'), (transporte, '250.00'),
                                  (vivienda, '1000.00'), (salud, '200.00')]:
            db.session.add(Presupuesto(categoria=categoria, monto_limite=Decimal(monto), mes=hoy.month, anio=hoy.year))
        proxima_fecha = hoy.replace(day=monthrange(hoy.year, hoy.month)[1])
        db.session.add(GastoRecurrente(subcategoria=servicios, cuenta=banco, monto=Decimal('160.00'),
                                     frecuencia='mensual', proxima_fecha=proxima_fecha))
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
