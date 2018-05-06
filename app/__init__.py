from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

from config import Configuration
app = Flask(__name__)
app.config.from_object(Configuration)

db.init_app(app)

from .v1 import v1_blueprint
app.register_blueprint(v1_blueprint, url_prefix='/api/v1')
