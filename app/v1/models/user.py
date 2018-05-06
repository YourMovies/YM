from flask_restplus import fields
from sqlalchemy.orm import relationship
from app.v1 import v1_api
from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean, default=False)
    from .film import Film
    films = relationship('Film', backref='user')

    user_resource_model = v1_api.model('User', {
        'id': fields.Integer(readOnly=True, description='The user unique identifier. ReadOnly.'),
        'username': fields.String(required=True, description='The username'),
        'password': fields.String(required=True, description='The user password'),
        'admin': fields.Boolean(readOnly=True, description='isAdmin. ReadOnly.')
    })
