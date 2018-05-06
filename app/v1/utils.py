from flask import request
from app.v1.models.user import User
from . import v1_api
from werkzeug.security import check_password_hash
from functools import wraps


# auth_required decorator
def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization

        if not auth or not auth.username or not auth.password:
            v1_api.abort(401, 'Could not verify')

        current_user = User.query.filter_by(username=auth.username).first()

        if not current_user:
            v1_api.abort(401, 'Could not verify')

        if check_password_hash(current_user.password, auth.password):
            return f(*args, **kwargs, current_user=current_user)

        v1_api.abort(401, 'Could not verify')

    return decorated
