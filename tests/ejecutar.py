"""Ejecutar pruebas de integración en una base MySQL temporal y aislada."""
import os
import secrets
import subprocess
import sys
from pathlib import Path

import pymysql
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')
nombre = 'sistask_test_' + secrets.token_hex(8)
conexion = pymysql.connect(
    host=os.getenv('MYSQL_HOST', '127.0.0.1'),
    user=os.getenv('MYSQL_USER', 'root'),
    password=os.getenv('MYSQL_PASSWORD', ''),
    port=int(os.getenv('MYSQL_PORT', '3306')),
    autocommit=True,
)
creada = False
try:
    with conexion.cursor() as cursor:
        cursor.execute(f'CREATE DATABASE `{nombre}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        creada = True
        cursor.execute(f'USE `{nombre}`')
        esquema = (ROOT / 'sql/dbgastos.sql').read_text(encoding='utf-8')
        # La base temporal ya está seleccionada; solo se ejecutan los CREATE TABLE.
        for sentencia in esquema.split(';'):
            if sentencia.strip().upper().startswith('CREATE TABLE'):
                cursor.execute(sentencia)
    entorno = os.environ.copy()
    entorno.update(MYSQL_DATABASE=nombre, PYTHONPATH=str(ROOT))
    subprocess.run([sys.executable, str(ROOT / 'tests/verificar_app.py')], cwd=ROOT, env=entorno, check=True)
    comando = [sys.executable, '-m', 'flask', '--app', 'app', 'cargar-ejemplos']
    subprocess.run(comando, cwd=ROOT, env=entorno, check=True)
    repeticion = subprocess.run(comando, cwd=ROOT, env=entorno, capture_output=True, text=True)
    assert repeticion.returncode != 0 and 'tablas están vacías' in repeticion.stderr
    with conexion.cursor() as cursor:
        cursor.execute(f'SELECT COUNT(*) FROM `{nombre}`.gastos')
        assert cursor.fetchone()[0] == 8
    print('Carga de ejemplos y protección contra duplicados: correctas.')
finally:
    if creada:
        with conexion.cursor() as cursor:
            cursor.execute(f'DROP DATABASE `{nombre}`')
    conexion.close()
