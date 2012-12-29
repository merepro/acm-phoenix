from tests import ACMTestCase
from flask import g, url_for

class UserViewTest(ACMTestCase):
    """Unit tests for the User views."""
    def test_requires_login(self):
        """Tests views that require a login redirect if no logged in user."""
        response = self.client.get('/profile/')
        print response
        self.assertRedirects(response, '/login/?next=%2Fprofile%2F')
        
