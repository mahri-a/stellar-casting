import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from flask_cors import CORS

from models import setup_db, Movie, Actor

def delete(class_name, id):
  class_object = class_name.query.get(id)

  if class_object:
    class_object.delete()

    return jsonify({
      'success': True,
      'deleted_id': id,
      'total_records': class_name.query.count()
    })

  else:
    abort(422)


def create_app(test_config=None):
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  @app.route('/movies')
  def get_movies():
    movies = Movie.query.order_by(Movie.id).all()

    return jsonify({
      'success': True,
      'movies': [movie.format() for movie in movies]
    })

  @app.route('/actors')
  def get_actors():
    actors = Actor.query.order_by(Actor.id).all()
    
    return jsonify({
      'success': True,
      'actors': [actor.format() for actor in actors]
    })

  @app.route('/movies/<int:id>', methods=['DELETE'])
  def delete_movie(id):
    return delete(Movie, id)


  @app.route('/actors/<int:id>', methods=['DELETE'])
  def delete_actor(id):
    return delete(Actor, id)


  @app.route('/movies', methods=['POST'])
  def add_movie():
    data = request.get_json()

    title = data.get('title')
    release_date = data.get('release_date')

    try:
      new_movie = Movie(title=title, release_date=release_date)
      new_movie.insert()

      return jsonify({
        'success': True,
        'added': new_movie.id,
        'total_records': Movie.query.count()
      })

    except Exception as error:
      print(error)      


  @app.route('/actors', methods=['POST'])
  def add_actor():
    data = request.get_json()

    name = data.get('name')
    age = data.get('age')
    gender = data.get('gender')

    try:
      new_actor = Actor(name=name, age=age, gender=gender)
      new_actor.insert()

      return jsonify({
        'success': True,
        'added': new_actor.id,
        'total_records': Actor.query.count()
      })
    except Exception as error:
      print(error)

  return app

app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)