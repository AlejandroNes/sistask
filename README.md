# Sistask

Proyecto base con Python, Flask-AppBuilder y MySQL. No instala ni modifica el servidor MySQL.

## Configuración

1. Activa el entorno virtual e instala las dependencias (si aún no están instaladas):

   ```bash
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

   Para crear el entorno en otra máquina: `python3 -m venv .venv`.

2. Crea la base de datos en tu instalación de MySQL, por ejemplo:

   ```sql
   CREATE DATABASE dbgastos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

   El esquema de las seis tablas se encuentra en `sql/dbgastos.sql`; puedes crearlo con `mysql < sql/dbgastos.sql`.

3. Copia la configuración y edita `.env` con las credenciales MySQL:

   ```bash
   cp .env.example .env
   python -c 'import secrets; print(secrets.token_hex(32))'
   ```

   Sustituye `SECRET_KEY` por la clave generada. El usuario de MySQL debe tener permisos sobre la base de datos. No compartas ni subas `.env`.

4. Crea el usuario administrador e inicia la aplicación:

   ```bash
   flask --app app fab create-admin
   flask --app app run
   ```

   Abre http://127.0.0.1:5000. Flask-AppBuilder crea sus tablas de seguridad al iniciar; la base de datos debe existir previamente. El servidor `flask run` es para desarrollo.
