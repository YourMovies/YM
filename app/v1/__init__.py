from flask import Blueprint
from flask_restplus import Api
from .exceptions import ValidationException

v1_blueprint = Blueprint('v1_blueprint', __name__)
v1_api = Api(v1_blueprint,
             title='YM REST API',
             version='1.0',
             description='Endpoints to YM...')

from .resources.auth import auth_ns
from .resources.film import film_ns
from .resources.user import user_ns


@v1_api.errorhandler(ValidationException)
def handle_validation_exception(error):
    return {'message': 'Validation error', 'errors': {error.error_field_name: error.message}}, 400


v1_api.add_namespace(auth_ns)
v1_api.add_namespace(film_ns)
v1_api.add_namespace(user_ns)

