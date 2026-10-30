"""Modelos del dominio de gastos, vinculados a las tablas de dbgastos."""

from sqlalchemy.dialects.mysql import INTEGER, SMALLINT, TINYINT

from app import db


class Categoria(db.Model):
    __tablename__ = 'categorias'

    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)

    subcategorias = db.relationship('Subcategoria', back_populates='categoria', passive_deletes='all')
    presupuestos = db.relationship('Presupuesto', back_populates='categoria', passive_deletes='all')

    def __str__(self):
        return self.nombre


class Subcategoria(db.Model):
    __tablename__ = 'subcategorias'

    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    categoria_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('categorias.id', name='fk_subcategorias_categoria'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)

    categoria = db.relationship('Categoria', back_populates='subcategorias')
    gastos = db.relationship('Gasto', back_populates='subcategoria', passive_deletes='all')
    gastos_recurrentes = db.relationship('GastoRecurrente', back_populates='subcategoria', passive_deletes='all')

    def __str__(self):
        return self.nombre


class Cuenta(db.Model):
    __tablename__ = 'cuentas'

    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    saldo_inicial = db.Column(db.Numeric(14, 2), nullable=False, server_default='0')

    gastos = db.relationship('Gasto', back_populates='cuenta', passive_deletes='all')
    gastos_recurrentes = db.relationship('GastoRecurrente', back_populates='cuenta', passive_deletes='all')

    def __str__(self):
        return self.nombre


class Gasto(db.Model):
    __tablename__ = 'gastos'
    __table_args__ = (db.CheckConstraint('monto > 0', name='chk_gastos_monto'),)

    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    subcategoria_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('subcategorias.id', name='fk_gastos_subcategoria'), nullable=False)
    cuenta_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('cuentas.id', name='fk_gastos_cuenta'), nullable=False)
    monto = db.Column(db.Numeric(14, 2), nullable=False)
    descripcion = db.Column(db.Text)
    fecha = db.Column(db.Date, nullable=False)

    subcategoria = db.relationship('Subcategoria', back_populates='gastos')
    cuenta = db.relationship('Cuenta', back_populates='gastos')

    def __str__(self):
        return self.descripcion or f'Gasto {self.id}'


class Presupuesto(db.Model):
    __tablename__ = 'presupuestos'
    __table_args__ = (
        db.CheckConstraint('monto_limite > 0', name='chk_presupuestos_monto'),
        db.CheckConstraint('mes BETWEEN 1 AND 12', name='chk_presupuestos_mes'),
        db.CheckConstraint('anio BETWEEN 1 AND 9999', name='chk_presupuestos_anio'),
        db.UniqueConstraint('categoria_id', 'mes', 'anio', name='uq_presupuestos_periodo'),
    )

    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    categoria_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('categorias.id', name='fk_presupuestos_categoria'), nullable=False)
    monto_limite = db.Column(db.Numeric(14, 2), nullable=False)
    mes = db.Column(TINYINT(unsigned=True), nullable=False)
    anio = db.Column(SMALLINT(unsigned=True), nullable=False)

    categoria = db.relationship('Categoria', back_populates='presupuestos')

    def __str__(self):
        return f'{self.categoria} - {self.mes:02d}/{self.anio}'


class GastoRecurrente(db.Model):
    __tablename__ = 'gastos_recurrentes'
    __table_args__ = (db.CheckConstraint('monto > 0', name='chk_recurrentes_monto'),)

    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    subcategoria_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('subcategorias.id', name='fk_recurrentes_subcategoria'), nullable=False)
    cuenta_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('cuentas.id', name='fk_recurrentes_cuenta'), nullable=False)
    monto = db.Column(db.Numeric(14, 2), nullable=False)
    frecuencia = db.Column(db.String(30), nullable=False)
    proxima_fecha = db.Column(db.Date, nullable=False)

    subcategoria = db.relationship('Subcategoria', back_populates='gastos_recurrentes')
    cuenta = db.relationship('Cuenta', back_populates='gastos_recurrentes')

    def __str__(self):
        return f'{self.subcategoria} - {self.frecuencia}'
