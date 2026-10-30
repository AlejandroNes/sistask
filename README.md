# Mis gastos

Aplicación local de gestión de gastos con Python, Flask-AppBuilder y MySQL. Incluye CRUD de categorías, subcategorías, cuentas, gastos, presupuestos y gastos recurrentes; un dashboard; tres reportes mensuales; y un clasificador local que sugiere subcategorías a partir de gastos anteriores. No usa servicios externos.

## Instalación

Requisitos: Python 3.9 o superior y un servidor MySQL en funcionamiento. Desde la carpeta del proyecto:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Crea la base de datos y sus seis tablas ejecutando el script con un usuario autorizado en MySQL (agrega `-u` y `-p` si tu instalación lo necesita):

```bash
mysql < sql/dbgastos.sql
```

El script usa `CREATE TABLE IF NOT EXISTS`: no actualiza tablas existentes si tienen una estructura distinta. Flask-AppBuilder crea además sus propias tablas de seguridad cuando se inicia la aplicación.

Copia la configuración de ejemplo y genera una clave secreta:

```bash
cp .env.example .env
python -c 'import secrets; print(secrets.token_hex(32))'
```

Edita `.env` y coloca el resultado en `SECRET_KEY`, junto con los datos de conexión a MySQL. No compartas ni subas este archivo. El usuario de MySQL debe tener permisos sobre `dbgastos`.

## Primer acceso

Crea un administrador local. El comando te pedirá **correo y contraseña** en la terminal; la contraseña no se mostrará al escribirla:

```bash
flask --app app crear-admin
```

Inicia la aplicación:

```bash
flask --app app run
```

Abre <http://127.0.0.1:5000/> e inicia sesión con el correo y la contraseña creados. La aplicación almacena las contraseñas como hashes PBKDF2. Para detener el servidor pulsa `Ctrl+C`. El servidor integrado es para desarrollo local.

## Uso

En el dashboard encontrarás enlaces para gestionar las seis tablas. Primero crea una categoría, después una subcategoría y una cuenta; con ellas ya podrás registrar gastos y gastos recurrentes. Los presupuestos se asignan por categoría y mes. Las relaciones existentes impiden eliminar registros que estén siendo utilizados.

La página de reportes permite filtrar gastos por categoría y por cuenta, comparar el presupuesto con lo gastado y descargar los tres reportes del período en PDF. El asistente usa un modelo Naive Bayes local: necesita al menos tres gastos con descripción en dos subcategorías distintas y palabras conocidas. La sugerencia se debe revisar antes de registrar un gasto; el asistente no crea ni modifica registros.

La aplicación tiene autenticación local y datos compartidos entre los usuarios autorizados; no implementa cuentas ni datos privados separados por usuario. No hay registro público ni recuperación de contraseña por correo.

## Comprobación del proyecto

Para ejecutar las pruebas de integración con MySQL:

```bash
python tests/ejecutar.py
```

El usuario de MySQL debe poder crear y eliminar una base temporal. Las pruebas crean una base con un nombre aleatorio, comprueban el inicio de sesión, los CRUD, las relaciones y los reportes, y eliminan esa base al terminar. No usan ni modifican los datos de `dbgastos`.

## Datos de ejemplo

Para cargar categorías, cuentas, gastos, presupuestos y un gasto recurrente de demostración:

```bash
flask --app app cargar-ejemplos
```

El comando solo funciona si las seis tablas de gastos están vacías. Los importes son ficticios y se registran en el mes actual.
