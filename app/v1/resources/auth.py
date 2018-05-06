from flask import request
from flask_restplus import Resource, Namespace, fields
from ..models.user import User
from app import db
from app.v1 import v1_api
from ..exceptions import ValidationException
from werkzeug.security import check_password_hash, generate_password_hash


auth_ns = Namespace('auth')

register_model = v1_api.model('Register', {
    'username': fields.String(required=True),
    'password': fields.String(required=True)
})


@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(register_model, validate=True)
    @auth_ns.marshal_with(User.user_resource_model)
    @auth_ns.response(400, 'username or password incorrect')
    def post(self):

        if User.query.filter_by(username=v1_api.payload['username']).first():
            raise ValidationException(error_field_name='username', message='This username is already exists')

        hashed_password = generate_password_hash(v1_api.payload['password'], method='sha256')

        user = User(
            username=v1_api.payload['username'],
            password=hashed_password,
            admin=True)

        db.session.add(user)
        db.session.commit()

        return user


@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.marshal_with(User.user_resource_model)
    def get(self):
        auth = request.authorization

        if not auth or not auth.username or not auth.password:
            v1_api.abort(401, 'Incorrect username or password')

        user = User.query.filter_by(username=auth.username).first()

        if not user:
            v1_api.abort(401, 'Incorrect username or password')

        if check_password_hash(user.password, auth.password):
            return user, 200

        auth_ns.abort(401, 'Incorrect username or password')



