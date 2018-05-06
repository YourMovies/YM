from flask_restplus import fields
from sqlalchemy import ForeignKey
from app import db
from app.v1 import v1_api


class Film(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
    name = db.Column(db.String(50))
    genre = db.Column(db.String(50))
    rating = db.Column(db.Integer)
    description = db.Column(db.String(10000))
    img = db.Column(db.String(1000))
    watched = db.Column(db.Boolean, default=False)

    film_resource_model = v1_api.model('Film', {
        'id': fields.Integer(readOnly=True, description='The film unique identifier. ReadOnly.'),
        'name': fields.String(required=True, description='The film name'),
        'genre': fields.String(required=True, description='The film genre'),
        'rating': fields.Integer(required=True, description='The film rating'),
        'description': fields.String(required=True, description='The film description'),
        'img': fields.String(required=True, description='The film url of img'),
        'watched': fields.Boolean(required=True, description='watched')
    })
