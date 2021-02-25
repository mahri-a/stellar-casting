import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Movie, Actor, association_table

casting_assistant = os.getenv('CASTING_ASSISTANT_JWT')
casting_director = os.getenv('CASTING_DIRECTOR_JWT')
executive_producer = os.getenv('EXECUTIVE_PRODUCER_JWT')


class StellarTestCase(unittest.TestCase):

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "stellar_test"
        self.database_path = 'postgresql+psycopg2://{}:{}@{}/{}'.format(
            'mahri', 'pass', '127.0.0.1:5432', self.database_name)
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
        """Executed after reach test"""
        pass


    #----------------------------------------------------------------------------#
    # Test GET endpoints
    #----------------------------------------------------------------------------#


    def test_get_paginated_movies(self):
        res = self.client().get('/movies', 
            headers={'Authorization': f'Bearer {casting_assistant}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['records'])

    
    def test_404_get_paginated_movies(self):
        """Test 404 sent when requesting beyond valid page."""
        res = self.client().get('/movies?page=1000',
            headers={'Authorization': f'Bearer {casting_assistant}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')


    def test_get_paginated_actors(self):
        res = self.client().get('/actors', 
            headers={'Authorization': f'Bearer {casting_assistant}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['records'])

    
    def test_404_get_paginated_actors(self):
        """Test 404 sent when requesting beyond valid page."""
        res = self.client().get('/actors?page=1000',
            headers={'Authorization': f'Bearer {casting_assistant}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')


    #----------------------------------------------------------------------------#
    # Test POST endpoints
    #----------------------------------------------------------------------------#


    def test_add_movie(self):
        res = self.client().post('/movies', 
            headers={'Authorization': f'Bearer {executive_producer}'},
            json=self.new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['added'])
        self.assertTrue(data['total_records'])


    def test_422_add_movie(self):
        """Test 422 sent when attempting to add a movie with a missing field."""
        res = self.client().post('/movies', 
            headers={'Authorization': f'Bearer {executive_producer}'},
            json={'title': 'Crouching Cat Hidden Turtle'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

     
  

        

        

    #----------------------------------------------------------------------------#
    # Test DELETE endpoints
    #----------------------------------------------------------------------------#
     
    #  def test_delete_movies(self):
    #     res = self.client().get('/movies/',
    #         headers={'Authorization': f'Bearer {casting_assistant}'})
    #     data = json.loads(res.data)




    



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
