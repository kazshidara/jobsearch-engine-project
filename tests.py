import unittest
from unittest import TestCase
import server 
from server import app, connect_to_db
from model import db, example_data


# 1. Integration Tests - Testing Flask Routes 

class TestFlaskRoutes(unittest.TestCase):
    """Test Flask routes."""

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True 
        connect_to_db(app, "test_database")
        
        db.create_all()
        example_data()

    def tearDown(self):
    #     """Stuff to do after every test."""

        db.session.remove()
        db.drop_all()
        db.engine.dispose()

    # TEST 1 - testing if index page is rendered correctly
    def test_index(self):
        """Make sure index page returns correct HTML - Header Text."""

        # Create a test client
        client = server.app.test_client()

        # Use the test client to make requests
        result = client.get('/')

        # Compare result.data with assert method
        self.assertIn(b'<h3>Enter a Job Title, Location or Both:</h3>', result.data)


    # TEST 2 - testing post requests when user logs into app
    def test_login(self):
        """Test login page"""

        client = server.app.test_client()
        result = self.client.post("/login", 
                              data = {"email": "test1@gmail.com", "password": "123"},
                              follow_redirects=True)

        self.assertIn(b"<h3>Enter a Job Title, Location or Both:</h3>", result.data)

        
    # TEST 3 - testing GET request

    # TEST 4 - testing API Calls 

    # TEST 5 - testing Flask and Database 



if __name__ == "__main__":

    unittest.main()
   