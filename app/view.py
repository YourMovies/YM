from app import app, db
from flask import request, jsonify, make_response, Markup
from models import User, Film
import uuid
# import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import feedparser



# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None

#         if 'x-access-token' in request.headers:
#             token = request.headers['x-access-token']

#         if not token:
#             return make_response('Token is missing!', 401)
#             # return jsonify({'message': 'Token is missing!'}), 401

#         try:
#             data = jwt.decode(token, app.config['SECRET_KEY'])
#             current_user = User.query.filter_by(public_id=data['public_id']).first()
#         except:
#             return jsonify({'message': 'Token is invalid!'}), 401

#         return f(current_user, *args, **kwargs)

#     return decorated


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization

        if not auth or not auth.username or not auth.password:
            return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required"'})

        current_user = User.query.filter_by(name=auth.username).first()

        if not current_user:
            return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required"'})

        if check_password_hash(current_user.password, auth.password):
            return f(current_user, *args, **kwargs)

        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required"'})

    return decorated


@app.route('/')
def index():

    rss = 'https://st.kp.yandex.net/rss/premiere.rss'

    feed = feedparser.parse(rss)
    items = feed.get('items', [])
    test = []

    if len(items):
        for item in items:
            test_data = {}
            test_data['summary'] = Markup(item['summary'])
            test_data['image'] = item['links'][1]['href']
            test_data['link'] = item['links'][0]['href']
            test_data['title'] = item['title']
            test.append(test_data)

    return jsonify({'title': feed['feed']['title'], 'data': test})


@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required"'})

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required"'})

    if check_password_hash(user.password, auth.password):
        make_response(jsonify({'user': user}), 200)

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required"'})



@app.route('/user', methods=['GET'])
@auth_required
def get_all_users(current_user):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})

    users = User.query.all()
    output = []

    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        output.append(user_data)

    return jsonify({'users': output})


@app.route('/user/<public_id>', methods=['GET'])
@auth_required
def get_one_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['admin'] = user.admin

    return jsonify({'user': user_data})


@app.route('/user', methods=['POST'])
@auth_required
def create_user(current_user):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})

    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=data['admin'])

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'New user created!'})


@app.route('/user/<public_id>', methods=['PUT'])
@auth_required
def promote_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})

    data = request.get_json()
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    hashed_password = generate_password_hash(data['password'], method='sha256')
    user.name = data['name']
    user.password = hashed_password
    user.admin = data['admin']

    db.session.commit()

    return jsonify({'message': 'The user has been promoted!'})


@app.route('/user/<public_id>', methods=['DELETE'])
@auth_required
def delete_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'The user has been deleted!'})


@app.route('/film', methods=['GET'])
@auth_required
def get_all_films(current_user):
    films = Film.query.filter_by(user_id=current_user.id).all()
    output = []

    for film in films:
        film_data = {}
        film_data['id'] = film.id
        film_data['name'] = film.name
        film_data['genre'] = film.genre
        output.append(film_data)

    return jsonify({'films': output})


@app.route('/film/<film_id>', methods=['GET'])
@auth_required
def get_one_film(current_user, film_id):
    film = Film.query.filter_by(id=film_id, user_id=current_user.id).first()

    if not film:
        return jsonify({'message': 'No film found!'})

    film_data = {}
    film_data['id'] = film.id
    film_data['name'] = film.name
    film_data['genre'] = film.genre

    return jsonify(film_data)


@app.route('/film', methods=['POST'])
@auth_required
def create_film(current_user):
    data = request.get_json()
    new_film = Film(name=data['name'], genre=data['genre'], user_id=current_user.id)
    db.session.add(new_film)
    db.session.commit()

    return jsonify({'message': 'Film created!'})


@app.route('/film/<film_id>', methods=['PUT'])
@auth_required
def complete_film(current_user, film_id):
    film = Film.query.filter_by(id=film_id, user_id=current_user.id).first()
    data = request.get_json()

    if not film:
        return jsonify({'message': 'No film found!'})

    film.name = data['name']
    film.genre = data['genre']
    db.session.commit()

    return jsonify({'message': 'Film has been completed!'})


@app.route('/film/<film_id>', methods=['DELETE'])
@auth_required
def delete_film(current_user, film_id):
    film = Film.query.filter_by(id=film_id, user_id=current_user.id).first()

    if not film:
        return jsonify({'message': 'No film found!'})

    db.session.delete(film)
    db.session.commit()

    return jsonify({'message': 'Film deleted!'})
