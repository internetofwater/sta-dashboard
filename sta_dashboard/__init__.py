import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

user = os.environ["POSTGRES_USER"]
password = os.environ["POSTGRES_PASSWORD"]
database = os.environ["POSTGRES_DB"] 

app.config['SQLALCHEMY_DATABASE_URI'] = \
    f'postgresql+psycopg2://{user}:{password}@postgres:5432/{database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from sta_dashboard import routes
