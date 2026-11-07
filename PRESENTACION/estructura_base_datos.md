# Estructura de la base de datos: Mis gastos

**Estudiantes:**

- Nestor Alejandro Mamani Condori
- Ariel Alvarez Mamani

La base de datos `dbgastos` organiza las categorías, cuentas, gastos y presupuestos de la aplicación. El siguiente diagrama muestra las seis tablas del dominio y sus relaciones.

```mermaid
erDiagram
    categorias ||--o{ subcategorias : contiene
    categorias ||--o{ presupuestos : tiene
    subcategorias ||--o{ gastos : clasifica
    cuentas ||--o{ gastos : registra
    subcategorias ||--o{ gastos_recurrentes : clasifica
    cuentas ||--o{ gastos_recurrentes : registra

    categorias {
        INT id PK
        VARCHAR nombre "Hasta 100 caracteres; obligatorio"
        TEXT descripcion "Opcional"
    }

    subcategorias {
        INT id PK
        INT categoria_id FK
        VARCHAR nombre "Hasta 100 caracteres; obligatorio"
    }

    cuentas {
        INT id PK
        VARCHAR nombre "Hasta 100 caracteres; obligatorio"
        DECIMAL saldo_inicial "14 digitos, 2 decimales; por defecto 0"
    }

    gastos {
        INT id PK
        INT subcategoria_id FK
        INT cuenta_id FK
        DECIMAL monto "14 digitos, 2 decimales; mayor que 0"
        TEXT descripcion "Opcional"
        DATE fecha
    }

    presupuestos {
        INT id PK
        INT categoria_id FK
        DECIMAL monto_limite "14 digitos, 2 decimales; mayor que 0"
        TINYINT mes "Entre 1 y 12"
        SMALLINT anio "Entre 1 y 9999"
    }

    gastos_recurrentes {
        INT id PK
        INT subcategoria_id FK
        INT cuenta_id FK
        DECIMAL monto "14 digitos, 2 decimales; mayor que 0"
        VARCHAR frecuencia "Hasta 30 caracteres"
        DATE proxima_fecha
    }
```

## Relaciones y reglas

- Una categoría puede tener varias subcategorías y varios presupuestos. Cada subcategoría y cada presupuesto pertenecen a una sola categoría.
- Una subcategoría y una cuenta pueden estar asociadas a varios gastos y gastos recurrentes. Cada gasto pertenece a una subcategoría y a una cuenta.
- Los identificadores son claves primarias autoincrementales y las claves foráneas conectan las tablas. Los campos son obligatorios salvo las descripciones indicadas como opcionales.
- Solo puede existir un presupuesto por categoría, mes y año. Los montos de gastos, gastos recurrentes y presupuestos deben ser mayores que cero.

El diagrama se basa en `sql/dbgastos.sql`. Flask-AppBuilder también crea tablas propias para la seguridad y la gestión de usuarios, que no se muestran aquí.
