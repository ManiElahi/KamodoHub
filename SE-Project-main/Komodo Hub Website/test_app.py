import unittest
import os
from app import app, get_db_connection

class KomodoHubTestCase(unittest.TestCase):
    def setUp(self):
        # Set up the test client
        app.config['TESTING'] = True
        self.client = app.test_client()
        # Optionally, configure a separate test database if needed

    def tearDown(self):
        # Clean up actions (if any) after each test
        pass

    def test_index_page(self):
        # Test that the homepage loads and contains expected text
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Endangered Species Overview', response.data)

    def test_register_page_get(self):
        # Test that the registration page loads
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

    def test_login_page_get(self):
        # Test that the login page loads
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_404_page(self):
        # Test that a non-existent route returns 404
        response = self.client.get('/nonexistent_route')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'404', response.data)

    def test_newsletter_subscription(self):
        # Test subscribing to the newsletter
        email = "test@example.com"
        response = self.client.post('/subscribe_newsletter', data={'email': email}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # Check if the flash message for subscription appears
        self.assertTrue(b"Thank you for subscribing" in response.data or b"already subscribed" in response.data)

if __name__ == '__main__':
    unittest.main()
