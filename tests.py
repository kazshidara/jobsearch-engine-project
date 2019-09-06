from unittest import TestCase
from server import app

# 1. Integration Tests - Testing Flask Routes 

class FlaskRoutes(TestCase):
    """Test Flask routes."""

    def setUp(self):
        """Stuff to do before every test."""
        self.client - app.test_client()
        app.config['TESTING'] = True 
        connect_to_db(app, "postgresql:///mydatabase")
        
        db.create_all()
        example_data()

    def tearDown(self):
        """Stuff to do after every test."""

        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        

    def test_index(self):
        """Make sure index page returns correct HTML - Header Text."""

        # Create a test client
        client = server.app.test_client()

        # Use the test client to make requests
        result = client.get('/')

        # Compare result.data with assert method
        self.assertIn(b'<h3>Enter a Job Title, Location or Both:</h3>', result.data)

    def test_user_profile(self):
        """Make sure user profile page returns correct HTML - Line Chart."""

        # Create a test client
        client = server.app.test_client()

        # Use the test client to make requests
        result = client.get('/user_profile')

        # Compare result.data with assert method
        self.assertIn(b'<canvas id="lineChart"></canvas>', result.data)



   