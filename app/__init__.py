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
    database=os.environ.get('MYSQL_DATABASE', 'sistask'),
    query={'charset': 'utf8mb4'},
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
with app.app_context():
    appbuilder = AppBuilder(app, db.session)
