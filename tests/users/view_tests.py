from tests import ACMTestCase
from flask import url_for, make_response
from flask.ext.login import current_user
from acm_phoenix.extensions import db
from acm_phoenix.views import mod as indexModule
from acm_phoenix.users.views import mod as usersModule
from acm_phoenix.users.views import verify_credentials_and_login
from acm_phoenix.users.decorators import oauth_flow
from acm_phoenix.users.models import User
from apiclient.http import HttpMockSequence

class UserViewTest(ACMTestCase):
    """Unit tests for the User views."""
    def test_login_required(self):
        """Tests views that require a login redirect if no current user."""
        response = self.client.get('/profile/')
        self.assertRedirects(response, url_for('users.login', next='/profile/'))

        response = self.client.get('/profile/edit/')
        self.assertRedirects(response,
                             url_for('users.login', next='/profile/edit/'))

        response = self.client.get('/verify/key')
        self.assertRedirects(response,
                             url_for('users.login', next='/verify/key'))

        response = self.client.get('/paymembership/')
        self.assertRedirects(response,
                             url_for('users.login', next='/paymembership/'))

        response = self.client.get('/user/view/id/')
        self.assertRedirects(response,
                             url_for('users.login', next='/user/view/id/'))

    @oauth_flow
    def test_login_redirect_to_google(flow, self):
        """Tests that navigation login view redirects to google oauth."""
        response = self.client.get('/login/')
        self.assertEquals(response.location, flow.step1_get_authorize_url())
                             
    @oauth_flow
    def test_verify_credentials_and_login(flow, self):
        """Tests if verify_credentials_and_login redirect properly."""
        # Create mock sequence to get credentials
        http = HttpMockSequence([
                ({'status': '200'},
                 """{ "access_token":"SlAV32hkKG",
                      "expires_in":3600,
                      "refresh_token":"8xLOxBtZp8" }"""),
                ])
        credentials = flow.step2_exchange('some random code', http=http)

        # Test that invalid credentials (missing id_token) abort.
        response = make_response(verify_credentials_and_login(credentials))
        self.assertEqual(response.location, url_for('index.show_home'))

        # Test that credentials with unverified emails abort to home page.
        credentials.id_token = dict(email='testu001@ucr.edu', 
                                    verified_email='false')
        response = make_response(verify_credentials_and_login(credentials))        
        self.assertEqual(response.location, url_for('index.show_home'))

        # Test that verified email redirects to register if non-existent user.
        credentials.id_token['verified_email'] = 'true'
        response = make_response(verify_credentials_and_login(credentials))
        self.assertEqual(response.location, url_for('users.register'))

        # Test that verified email redirects to profile if user exists.
        user = User(email='testu001@ucr.edu')
        db.session.add(user)
        db.session.commit()
        response = make_response(verify_credentials_and_login(credentials))
        self.assertEqual(response.location, url_for('users.home'))

        # User should now be logged into session.
        self.assertTrue(current_user.is_authenticated())

        # current_user's id should match user's id.
        user = User.query.filter_by(email='testu001@ucr.edu').first()
        self.assertEqual(user.id, current_user.id)
