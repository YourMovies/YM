from flask_restplus import Resource, Namespace
from app import db
from app.v1 import v1_api
from ..utils import auth_required
from ..models.user import User as UserModel
from werkzeug.security import generate_password_hash


user_ns = Namespace('user')


@user_ns.route('/')
class UserList(Resource):
    @user_ns.response(200, 'Success')
    @user_ns.marshal_with(UserModel.user_resource_model)
    @auth_required
    def get(self, current_user):
        if not current_user.admin:
            user_ns.abort(403, 'Cannot perform that function')

        users = UserModel.query.all()
        if users:
            return users, 200

        user_ns.abort(404, 'Users not found or you don\'t have permission to view it')


@user_ns.route('/<int:id>')
class User(Resource):
    @user_ns.response(200, 'Success')
    @user_ns.marshal_with(UserModel.user_resource_model)
    @auth_required
    def get(self, id, current_user):
        if not current_user.admin:
            user_ns.abort(403, 'Cannot perform that function')

        user = UserModel.query.filter_by(id=id).first()
        if user:
            return user, 200

        user_ns.abort(404, 'User not found or you don\'t have permission to view it')

    @user_ns.response(200, 'Success')
    @user_ns.expect(UserModel.user_resource_model, validate=True)
    @user_ns.marshal_with(UserModel.user_resource_model)
    @auth_required
    def put(self, id, current_user):
        if not current_user.admin:
            user_ns.abort(403, 'Cannot perform that function')

        user = UserModel.query.filter_by(id=id).first()
        if user:
            try:
                username = v1_api.payload['username']
                password = v1_api.payload['password']
            except KeyError:
                username = user.username
                password = user.password

            hashed_password = generate_password_hash(password, method='sha256')

            user.username = username
            user.password = hashed_password

            db.session.add(user)
            db.session.commit()

            return user, 200

        user_ns.abort(404, 'User not found or you don\'t have permission to view it')

    @user_ns.response(204, 'User deleted')
    @auth_required
    def delete(self, id, current_user):
        if not current_user.admin:
            user_ns.abort(403, 'Cannot perform that function')

        user = UserModel.query.filter_by(id=id).first()
        if user:
            db.session.delete(user)
            db.session.commit()

            return '', 204

        user_ns.abort(404, 'User not found or you don\'t have permission to view it')



