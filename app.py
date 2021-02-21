from flask import Flask, request, abort, jsonify
from flask_cors import CORS

from models import setup_db, Movie, Actor
from auth import AuthError, requires_auth


def get_records(Model):
  objects = Model.query.order_by(Model.id).all()

  return jsonify({
    'success': True,
    'records': [obj.format() for obj in objects],
    'total_records': Model.query.count()
  })


def delete(Model, id):
  obj = Model.query.get(id)

  if obj:
    obj.delete()

    return jsonify({
      'success': True,
      'deleted': obj.format(),
      'total_records': Model.query.count()
    })

  else:
    abort(404)


def add(Model, request, col_list):
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
    abort(422, description='Data is required')


def modify(Model, id, request, col_list):
  obj = Model.query.get(id)
  data = request.get_json()

  if obj:
    if data:
      attrs = {}
      for k in col_list:
        value = data.get(k)
        if value:
          attrs[k] = value 

      try:
        obj.update(attrs)

        return jsonify({
          'succes': True,
          'updated': obj.format()
        })
      except Exception as e:
        print(repr(e))
        abort(422)

    else:
      abort(422, description='Data is required')

  else:
    abort(404)      


def create_app(test_config=None):
  app = Flask(__name__)
  setup_db(app)
  CORS(app)


  #----------------------------------------------------------------------------#
  # Controllers
  #----------------------------------------------------------------------------#


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
    return add(Movie, request, ['title', 'release_date'])   


  @app.route('/actors', methods=['POST'])
  @requires_auth('post:actors')
  def add_actor(payload):
    return add(Actor, request, ['name', 'age', 'gender'])


  @app.route('/movies/<int:id>', methods=['PATCH'])
  @requires_auth('patch:movies')
  def modify_movie(payload, id):
    return modify(Movie, id, request, ['title', 'release_date'])


  @app.route('/actors/<int:id>', methods=['PATCH'])
  @requires_auth('patch:actors')
  def modify_actor(payload, id):
    return modify(Actor, id, request, ['name', 'age', 'gender'])


  #----------------------------------------------------------------------------#
  # Error Handlers
  #----------------------------------------------------------------------------#


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
      'message': ex.error['code']
      'description': ex.error['description']
    }), ex.status_code


  return app

app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)