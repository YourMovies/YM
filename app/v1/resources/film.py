from flask_restplus import Resource, Namespace
from app import db
from app.v1 import v1_api
from ..utils import auth_required
from ..models.film import Film as FilmModel


film_ns = Namespace('film')


@film_ns.route('/')
class FilmList(Resource):
    @film_ns.response(200, 'Success')
    @film_ns.marshal_with(FilmModel.film_resource_model)
    @auth_required
    def get(self, current_user):
        films = FilmModel.query.filter_by(user_id=current_user.id).all()
        if films:
            return films, 200

        film_ns.abort(404, 'Films not found or you don\'t have permission to view it')

    @film_ns.response(200, 'Success')
    @film_ns.expect(FilmModel.film_resource_model, validate=True)
    @film_ns.marshal_with(FilmModel.film_resource_model)
    @auth_required
    def post(self, current_user):
        try:
            name = v1_api.payload['name']
            genre = v1_api.payload['genre']
            rating = v1_api.payload['rating']
            description = v1_api.payload['description']
            img = v1_api.payload['img']
            watched = v1_api.payload['watched']
        except KeyError:
            name = ''
            genre = ''
            rating = 0
            description = ''
            img = ''
            watched = False

        film = FilmModel(
                name=name,
                genre=genre,
                rating=rating,
                description=description,
                img=img,
                watched=watched,
                user_id=current_user.id)

        db.session.add(film)
        db.session.commit()

        return film, 200


@film_ns.route('/<int:id>')
class Film(Resource):
    @film_ns.response(200, 'Success')
    @film_ns.marshal_with(FilmModel.film_resource_model)
    @auth_required
    def get(self, id, current_user):
        film = FilmModel.query.filter_by(user_id=current_user.id, id=id).first()
        if film:
            return film, 200

        film_ns.abort(404, 'Films not found or you don\'t have permission to view it')

    @film_ns.response(200, 'Success')
    @film_ns.expect(FilmModel.film_resource_model, validate=True)
    @film_ns.marshal_with(FilmModel.film_resource_model)
    @auth_required
    def put(self, id, current_user):
        film = FilmModel.query.filter_by(user_id=current_user.id, id=id).first()
        if film:
            try:
                name = v1_api.payload['name']
                genre = v1_api.payload['genre']
                rating = v1_api.payload['rating']
                description = v1_api.payload['description']
                img = v1_api.payload['img']
                watched = v1_api.payload['watched']
            except KeyError:
                name = film.name
                genre = film.genre
                rating = film.rating
                description = film.description
                img = film.img
                watched = film.watched

            film.name = name
            film.genre = genre
            film.rating = rating
            film.description = description
            film.img = img
            film.watched = watched

            db.session.add(film)
            db.session.commit()

            return film, 200

        film_ns.abort(404, 'Films not found or you don\'t have permission to view it')

    @film_ns.response(200, 'Success')
    @auth_required
    def delete(self, id, current_user):
        film = FilmModel.query.filter_by(user_id=current_user.id, id=id).first()

        if film:
            db.session.delete(film)
            db.session.commit()

            return '', 204

        film_ns.abort(404, 'Films not found or you don\'t have permission to view it')