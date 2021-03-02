import os
from flask import Flask, request, abort, jsonify
from flask_cors import CORS

from models import setup_db, Movie, Actor
from auth import AuthError, requires_auth

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
API_AUDIENCE = os.getenv('API_AUDIENCE')
AUTH0_CLIENT_ID = os.getenv('AUTH0_CLIENT_ID')
AUTH0_CALLBACK_URL = os.getenv('AUTH0_CALLBACK_URL')


def paginate(query):
    items_limit = request.args.get('limit', 5, type=int)
    selected_page = request.args.get('page', 1, type=int)
    current_index = selected_page - 1

    selection = query.limit(items_limit).offset(
                            current_index * items_limit).all()
    records = [record.format() for record in selection]

    return records


def get_records(Model):
    query = Model.query.order_by(Model.id)
    records = paginate(query)

    if len(records) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'records': records,
        'total_records': Model.query.count()
    })


def delete(Model, id):
    record = Model.query.get(id)

    if record:
        record.delete()

        return jsonify({
          'success': True,
          'deleted': record.format(),
          'total_records': Model.query.count()
        })

    else:
        abort(404)


def add(Model, col_list):
    data = request.get_json()

    if data:
        kwargs = {}
        for k in col_list:
            value = data.get(k)
            if value:
                kwargs[k] = value
            else:
                abort(422, description=f'{k} is required')

        try:
            entry = Model(**kwargs)
            entry.insert()

            return jsonify({
              'success': True,
              'added': entry.format(),
              'total_records': Model.query.count()
            })

        except Exception as e:
            print(repr(e))
            abort(422)

    else:
        abort(400)


def modify(Model, id, col_list):
    record = Model.query.get(id)
    data = request.get_json()

    if record:
        if data:
            attrs = {}
            for k in col_list:
                value = data.get(k)
                if value:
                    attrs[k] = value

            try:
                record.update(attrs)

                return jsonify({
                  'success': True,
                  'updated': record.format()
                })

            except Exception as e:
                print(repr(e))
                abort(422)

        else:
            abort(400)

    else:
        abort(404)


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # ----------------------------------------------------------------#
    # Controllers
    # ----------------------------------------------------------------#

    @app.route('/')
    def index():
        return jsonify({'message': 'Hello world, this is Stellar Casting.'})

    # helper to get access token
    @app.route("/authorization/url", methods=["GET"])
    def generate_auth_url():
        url = f'https://{AUTH0_DOMAIN}/authorize' \
            f'?audience={API_AUDIENCE}' \
            f'&response_type=token&client_id=' \
            f'{AUTH0_CLIENT_ID}&redirect_uri=' \
            f'{AUTH0_CALLBACK_URL}'

        return jsonify({
            'url': url
        })

    @app.route('/movies', methods=['GET'])
    @requires_auth('get:movies')
    def get_movies(payload):
        return get_records(Movie)

    @app.route('/actors', methods=['GET'])
    @requires_auth('get:actors')
    def get_actors(payload):
        return get_records(Actor)

    @app.route('/movies/<int:id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movie(payload, id):
        return delete(Movie, id)

    @app.route('/actors/<int:id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actor(payload, id):
        return delete(Actor, id)

    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movies')
    def add_movie(payload):
        return add(Movie, ['title', 'release_date'])

    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actors')
    def add_actor(payload):
        return add(Actor, ['name', 'age', 'gender'])

    @app.route('/movies/<int:id>', methods=['PATCH'])
    @requires_auth('patch:movies')
    def modify_movie(payload, id):
        return modify(Movie, id, ['title', 'release_date'])

    @app.route('/actors/<int:id>', methods=['PATCH'])
    @requires_auth('patch:actors')
    def modify_actor(payload, id):
        return modify(Actor, id, ['name', 'age', 'gender'])

    # ----------------------------------------------------------------#
    # Error Handlers
    # ----------------------------------------------------------------#

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not found',
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method not allowed'
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable',
            'description': error.description
        }), 422

    @app.errorhandler(AuthError)
    def authentification_fail(ex):
        return jsonify({
          'success': False,
          'error': ex.status_code,
          'code': ex.error['code'],
          'description': ex.error['description']
        }), ex.status_code

    return app

app = create_app()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
