CREATE DATABASE IF NOT EXISTS dbgastos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE dbgastos;

CREATE TABLE IF NOT EXISTS categorias (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS subcategorias (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    categoria_id INT UNSIGNED NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    CONSTRAINT fk_subcategorias_categoria FOREIGN KEY (categoria_id) REFERENCES categorias(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS cuentas (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    saldo_inicial DECIMAL(14, 2) NOT NULL DEFAULT 0
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS gastos (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    subcategoria_id INT UNSIGNED NOT NULL,
    cuenta_id INT UNSIGNED NOT NULL,
    monto DECIMAL(14, 2) NOT NULL,
    descripcion TEXT,
    fecha DATE NOT NULL,
    CONSTRAINT chk_gastos_monto CHECK (monto > 0),
    CONSTRAINT fk_gastos_subcategoria FOREIGN KEY (subcategoria_id) REFERENCES subcategorias(id),
    CONSTRAINT fk_gastos_cuenta FOREIGN KEY (cuenta_id) REFERENCES cuentas(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS presupuestos (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    categoria_id INT UNSIGNED NOT NULL,
    monto_limite DECIMAL(14, 2) NOT NULL,
    mes TINYINT UNSIGNED NOT NULL,
    anio SMALLINT UNSIGNED NOT NULL,
    CONSTRAINT chk_presupuestos_monto CHECK (monto_limite > 0),
    CONSTRAINT chk_presupuestos_mes CHECK (mes BETWEEN 1 AND 12),
    CONSTRAINT chk_presupuestos_anio CHECK (anio BETWEEN 1 AND 9999),
    CONSTRAINT uq_presupuestos_periodo UNIQUE (categoria_id, mes, anio),
    CONSTRAINT fk_presupuestos_categoria FOREIGN KEY (categoria_id) REFERENCES categorias(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS gastos_recurrentes (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    subcategoria_id INT UNSIGNED NOT NULL,
    cuenta_id INT UNSIGNED NOT NULL,
    monto DECIMAL(14, 2) NOT NULL,
    frecuencia VARCHAR(30) NOT NULL,
    proxima_fecha DATE NOT NULL,
    CONSTRAINT chk_recurrentes_monto CHECK (monto > 0),
    CONSTRAINT fk_recurrentes_subcategoria FOREIGN KEY (subcategoria_id) REFERENCES subcategorias(id),
    CONSTRAINT fk_recurrentes_cuenta FOREIGN KEY (cuenta_id) REFERENCES cuentas(id)
) ENGINE=InnoDB;
