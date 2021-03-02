import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Movie, Actor


DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
DB_HOST = os.getenv('DB_HOST', '127.0.0.1:5432')

casting_assistant = os.getenv('CASTING_ASSISTANT_JWT')
casting_director = os.getenv('CASTING_DIRECTOR_JWT')
executive_producer = os.getenv('EXECUTIVE_PRODUCER_JWT')


class StellarTestCase(unittest.TestCase):

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = 'stellar_test'
        self.database_path = 'postgresql://{}:{}@{}/{}'.format(
            DB_USER, DB_PASSWORD, DB_HOST, self.database_name)
        setup_db(self.app, self.database_path)

        self.new_movie = {
            'title': 'The Incredibles 3',
            'release_date': '2021-02-28'
        }

        self.new_actor = {
            'name': 'Rob Boss',
            'age': 30,
            'gender': 'M'
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after each test"""
        pass

    # ----------------------------------------------------------------#
    # Test GET endpoints
    # ----------------------------------------------------------------#
    # All roles can view actors and movies

    def test_get_paginated_movies(self):
        res = self.client().get(
            '/movies',
            headers={'Authorization': f'Bearer {casting_assistant}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['records'])

    def test_404_get_paginated_movies(self):
        """Test 404 sent when requesting beyond valid page."""
        res = self.client().get(
            '/movies?page=1000',
            headers={'Authorization': f'Bearer {casting_assistant}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_get_paginated_actors(self):
        res = self.client().get(
            '/actors',
            headers={'Authorization': f'Bearer {casting_assistant}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['records'])

    def test_404_get_paginated_actors(self):
        """Test 404 sent when requesting beyond valid page."""
        res = self.client().get(
            '/actors?page=1000',
            headers={'Authorization': f'Bearer {casting_assistant}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_get_movie_cast(self):
        res = self.client().get(
            '/movies/3/actors',
            headers={'Authorization': f'Bearer {casting_director}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movie_title'])
        self.assertTrue(data['actors'])
        self.assertTrue(data['total_actors'])

    def test_404_get_movie_cast(self):
        """Test 404 sent when requesting a nonexistent movie."""
        res = self.client().get(
            '/movies/1000/actors',
            headers={'Authorization': f'Bearer {casting_director}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_401_get_actors(self):
        """Test 401 sent when authorization header is missing."""
        res = self.client().get('/actors')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['code'], 'authorization_header_missing')
        self.assertEqual(data[
            'description'], 'Authorization header is expected.')

    # ----------------------------------------------------------------#
    # Test POST endpoints
    # ----------------------------------------------------------------#
    # Casting director can add actors
    # Executive producer can add actors and movies

    def test_add_movie(self):
        res = self.client().post(
            '/movies',
            headers={'Authorization': f'Bearer {executive_producer}'},
            json=self.new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['added'])

    def test_422_add_movie(self):
        """
        Test 422 sent when attempting to add
        a movie with a missing field.
        """
        res = self.client().post(
            '/movies',
            headers={'Authorization': f'Bearer {executive_producer}'},
            json={'title': 'Crouching Cat Hidden Turtle'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    def test_add_actor(self):
        res = self.client().post(
            '/actors',
            headers={'Authorization': f'Bearer {casting_director}'},
            json=self.new_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['added'])

    def test_422_add_actor(self):
        """
        Test 422 sent when attempting to add
        an actor with a missing field.
        """
        res = self.client().post(
            '/actors',
            headers={'Authorization': f'Bearer {casting_director}'},
            json={'name': 'Bob Ross', 'gender': 'M'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    def test_assign_actor(self):
        res = self.client().post(
            '/movies/1/actors',
            headers={'Authorization': f'Bearer {casting_director}'},
            json={'id': 3})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['assigned'])
        self.assertTrue(data['to_movie'])

    def test_400_assign_movie(self):
        """
        Test 400 sent when attempting to assign
        an actor to a nonexistent movie.
        """
        res = self.client().post(
            '/movies/1000/actors',
            headers={'Authorization': f'Bearer {casting_director}'},
            json={'id': 2})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request')

    # ----------------------------------------------------------------#
    # Test PATCH endpoints
    # ----------------------------------------------------------------#
    # Casting director and executive producer can modify actors and movies

    def test_modify_movie(self):
        res = self.client().patch(
            '/movies/2',
            headers={'Authorization': f'Bearer {casting_director}'},
            json={'release_date': '2020-02-02'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['updated'])

    def test_400_modify_movie(self):
        """Test 400 sent when json body is not provided."""
        res = self.client().patch(
            '/movies/2',
            headers={'Authorization': f'Bearer {casting_director}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request')

    def test_modify_actor(self):
        res = self.client().patch(
            '/actors/2',
            headers={'Authorization': f'Bearer {casting_director}'},
            json={'name': 'Keanu Beeves', 'age': 20})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['updated'])

    def test_404_modify_actor(self):
        """Test 404 sent when requesting a nonexistent actor."""
        res = self.client().patch(
            '/actors/1000',
            headers={'Authorization': f'Bearer {casting_director}'},
            json={'name': 'Sarah Connor'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    # ----------------------------------------------------------------#
    # Test DELETE endpoints
    # ----------------------------------------------------------------#
    # Casting director can delete actors
    # Executive producer can delete actors and movies

    def test_delete_movie(self):
        res = self.client().delete(
            '/movies/1',
            headers={'Authorization': f'Bearer {executive_producer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['deleted'])

    def test_404_delete_movie(self):
        """Test 404 sent when requesting a nonexistent movie."""
        res = self.client().delete(
            '/movies/1000',
            headers={'Authorization': f'Bearer {executive_producer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_delete_actor(self):
        res = self.client().delete(
            '/actors/1',
            headers={'Authorization': f'Bearer {casting_director}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['deleted'])

    def test_404_delete_actor(self):
        """Test 404 sent when requesting a nonexistent actor."""
        res = self.client().delete(
            '/actors/1000',
            headers={'Authorization': f'Bearer {casting_director}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    # ----------------------------------------------------------------#
    # Test RBAC for casting assistant
    # ----------------------------------------------------------------#
    # Casting assistant can only view actors and movies

    def test_add_movie_casting_assistant(self):
        res = self.client().post(
            '/movies',
            headers={'Authorization': f'Bearer {casting_assistant}'},
            json=self.new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['code'], 'invalid_payload')
        self.assertEqual(
            data['description'], 'Requested permission not in payload.')

    def test_delete_actor_casting_assistant(self):
        res = self.client().delete(
            '/actors/3',
            headers={'Authorization': f'Bearer {casting_assistant}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['code'], 'invalid_payload')
        self.assertEqual(
            data['description'], 'Requested permission not in payload.')

    # ----------------------------------------------------------------#
    # Test RBAC for casting director
    # ----------------------------------------------------------------#
    # Casting director cannot add or delete a movie

    def test_add_movie_casting_director(self):
        res = self.client().post(
            '/movies',
            headers={'Authorization': f'Bearer {casting_director}'},
            json=self.new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['code'], 'invalid_payload')
        self.assertEqual(
            data['description'], 'Requested permission not in payload.')

    def test_delete_movie_casting_director(self):
        res = self.client().delete(
            '/movies/3',
            headers={'Authorization': f'Bearer {casting_director}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['code'], 'invalid_payload')
        self.assertEqual(
            data['description'], 'Requested permission not in payload.')

    # ----------------------------------------------------------------#
    # Test RBAC for executive producer
    # ----------------------------------------------------------------#
    # Executive producer has all permissions

    def test_modify_movie_executive_producer(self):

        res = self.client().patch(
            '/movies/2',
            headers={'Authorization': f'Bearer {executive_producer}'},
            json={'release_date': '1998-05-15'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['updated'])

    def test_add_actor_executive_producer(self):
        res = self.client().post(
            '/actors',
            headers={'Authorization': f'Bearer {executive_producer}'},
            json=self.new_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['added'])


if __name__ == "__main__":
    unittest.main()
