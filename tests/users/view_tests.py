from tests import ACMTestCase
from flask import url_for, make_response, session
from flask.ext.login import current_user, login_user, logout_user
from acm_phoenix.extensions import db
from acm_phoenix.views import mod as indexModule
from acm_phoenix.users.views import mod as usersModule
from acm_phoenix.users.views import (verify_credentials_and_login,
                                     wepay_membership_response)
from acm_phoenix.users.decorators import oauth_flow
from acm_phoenix.users.models import User
from apiclient.http import HttpMockSequence
from oauth2client.client import FlowExchangeError

class UserViewTest(ACMTestCase):
    """Unit tests for the User views."""
    @oauth_flow
    def test_oauth_flow_object_is_valid(flow, self):
        """Tests the functions decorated with oauth_flow get valid object."""
        self.assertIsNotNone(flow)

    def test_login_required(self):
        """Tests views that require a login redirect if no current user."""
        # Convenient url holders
        profile_url = url_for('users.home')
        edit_url = url_for('users.edit_profile')
        verify_url = url_for('users.verify_membership_payment',
                             verification_key='key')
        payment_url = url_for('users.payment_redirect')
        view_url = url_for('users.view_profile', user_netid='id')
        
        def append_to_login_url(url):
            return url_for('users.login', next=url)

        # Tests with no current user should all redirect to users.login.
        response = self.client.get(profile_url)
        self.assertRedirects(response, append_to_login_url(profile_url))

        response = self.client.get(edit_url)
        self.assertRedirects(response, append_to_login_url(edit_url))

        response = self.client.get(verify_url)
        self.assertRedirects(response, append_to_login_url(verify_url))

        response = self.client.get(payment_url)
        self.assertRedirects(response, append_to_login_url(payment_url))

        response = self.client.get(view_url)
        self.assertRedirects(response, append_to_login_url(view_url))

        # Tests with current_user.
        # Access client's session to log in user.
        with self.client.session_transaction() as sess:
            user = User("Test User", "testu001", "testuser@ucr.edu", "S", "CS",
                        "M", "test user", "testsig")
            db.session.add(user)
            db.session.commit()
            login_user(user)
            sess['user_id'] = user.id

        response = self.client.get(profile_url)
        self.assert200(response)

        response = self.client.get(edit_url)
        self.assert200(response)

        response = self.client.get(verify_url)
        self.assertRedirects(response, profile_url)

        response = self.client.get(payment_url)
        """We don't know exactly where payment_redirect will direct to because
        calls to wepay_api give different responses."""
        print current_user.email
        self.assert_status(response, 302)

        response = self.client.get(view_url, follow_redirects=True)
        self.assert200(response)

        logout_user()
                             
    def test_home(self):
        """Tests home function renders properly with logged in user."""
        with self.client.session_transaction() as sess:
            user = User("Test User", "testu001", "testu001@ucr.edu", "S", "CS",
                        "M", "test user", "testsig")
            db.session.add(user)
            db.session.commit()
            login_user(user)
            sess['user_id'] = user.id

        response = self.client.get(url_for('users.home'))
        self.assert200(response)
        self.assertTemplateUsed('users/profile.html')
        self.assertContext('user', current_user)

        logout_user()

    def test_edit_profile(self):
        """Tests that user profile can be edited."""
        with self.client.session_transaction() as sess:
            user = User("Test User", "testu001", "testu001@ucr.edu", "soph",
                        "CS", "M", "test user", "testsig")
            db.session.add(user)
            db.session.commit()
            login_user(user)
            sess['user_id'] = user.id

        response = self.client.get(url_for('users.edit_profile'))
        self.assert200(response)
        self.assertTemplateUsed('users/edit.html')

        # Valid edit form update.
        form_data = {
            'name': 'Another Test',
            'netid': current_user.netid,
            'email': current_user.email,
            'shirt_size': current_user.shirt_size,
            'major': current_user.major,
            'standing': current_user.standing
        }
        response = self.client.post(url_for('users.edit_profile'),
                                    data=form_data, follow_redirects=True)
        self.assert200(response)
        self.assertTemplateUsed('users/profile.html')
        self.assertEquals(current_user.name, 'Another Test')

        # Invalid edit form data.
        form_data = {
            'name': 'Another Test',
            'netid': current_user.netid,
            'email': current_user.email,
            'shirt_size': current_user.shirt_size,
            'major': current_user.major,
            'standing': 'S' # should be 'senior', not 'S'
        }
        response = self.client.post(url_for('users.edit_profile'),
                                    data=form_data, follow_redirects=True)
        self.assert200(response)
        self.assertTemplateUsed('users/edit.html')
        self.assertEquals(current_user.standing, 'soph')
        self.assertIn('ul class="errors"', response.data)

        # Trying to change netid or email to another user's fails.
        user = User("Test User", "testu002", "testu002@ucr.edu", "soph",
                    "CS", "M", "test user", "testsig")
        db.session.add(user)
        db.session.commit()

        form_data = {
            'name': current_user.name,
            'netid': user.netid,
            'email': user.email,
            'shirt_size': current_user.shirt_size,
            'major': current_user.major,
            'standing': current_user.standing
        }
        response = self.client.post(url_for('users.edit_profile'),
                                    data=form_data, follow_redirects=True)
        self.assert200(response)
        self.assertTemplateUsed('users/profile.html')
        self.assertEquals(current_user.netid, 'testu001')
        self.assertEquals(current_user.email, 'testu001@ucr.edu')
        self.assertIn('You seem to be trying to change your netid/email',
                      response.data)

        logout_user()

    @oauth_flow
    def test_login(flow, self):
        """Tests that login view redirects properly."""

        # Test that login redirects to oauth2 flow with no current_user.
        response = self.client.get(url_for('users.login'))
        self.assertStatus(response, 302)
        self.assertEquals(response.location, flow.step1_get_authorize_url())

        with self.client.session_transaction() as sess:
            user = User("Test User", "testu001", "testu001@ucr.edu", "S", "CS",
                        "M", "test user", "testsig")
            db.session.add(user)
            db.session.commit()
            login_user(user)
            sess['user_id'] = user.id

        # Test that login redirects home if no next location is specified.
        response = self.client.get(url_for('users.login'), follow_redirects=True)
        self.assert200(response)
        self.assertTemplateUsed('users/profile.html')

        # Test that login redirects to next path if specified.
        response = self.client.get(url_for('users.login',
                                           next=url_for('index.show_home')),
                                   follow_redirects=True)
        self.assert200(response)
        self.assertTemplateUsed('home.html')
        
        logout_user()

    def test_wepay_membership_response(self):
        """Tests that wepay_membership_response gives a valid response and
        modifies the user object passed in."""
        user = User("Test User", "testu001", "testu001@ucr.edu", "S", "CS",
                    "M", "test user", "testsig")

        self.assertIsNone(user.wepay_verification)
        response = wepay_membership_response(user)
        self.assertIsNotNone(user.wepay_verification)
        self.assertIn('wepay.com', response['checkout_uri'])

    def test_register(self):
        """Tests registration view."""
        response = self.client.get(url_for('users.register'))
        self.assert200(response)
        self.assertTemplateUsed('users/register.html')

        # Posting with no form data.
        response = self.client.post(url_for('users.register'))
        self.assert200(response)
        self.assertTemplateUsed('users/register.html')
        self.assertIn('ul class="errors"', response.data)

        # Posting invalid form data.
        form_data = {
            'name': 'Test User',
            'netid': 'testu001',
            'email': 'testu001@ucr.edu',
            'shirt_size': 'M',
            'major': 'CS',
            'standing': 'S' # should be 'senior', not 'S'
        }
        response = self.client.post(url_for('users.register'), data=form_data)
        self.assert200(response)
        self.assertTemplateUsed('users/register.html')
        self.assertIn('ul class="errors"', response.data)

        # Valid form data.
        form_data = {
            'name': 'Test User',
            'netid': 'testu001',
            'email': 'testu001@ucr.edu',
            'shirt_size': 'M',
            'major': 'CS',
            'standing': 'soph',
            'output': 'randombase64'
        }

        # Should log in user and redirect to profile.
        response = self.client.post(url_for('users.register'), data=form_data,
                                        follow_redirects=True)
        self.assert200(response)
        self.assertTemplateUsed('users/profile.html')
        user = User.query.filter_by(email=form_data['email']).first()
        self.assertIsNotNone(user)
        self.assertTrue(user.member)
        self.assertIn('data:image/png;base64', user.signature)
        self.assertIn('Thanks for registering', response.data)

        db.session.delete(user)
        db.session.commit()

        # Valid form data with base64 encoded image as sigpad output.
        form_data = {
            'name': 'Test User',
            'netid': 'testu001',
            'email': 'testu001@ucr.edu',
            'shirt_size': 'M',
            'major': 'CS',
            'standing': 'soph',
            'output': 'data:image/png;base64,randombase64'
        }

        response = self.client.post(url_for('users.register'), data=form_data,
                                        follow_redirects=True)
        self.assert200(response)
        self.assertTemplateUsed('users/profile.html')
        user = User.query.filter_by(email=form_data['email']).first()
        self.assertIsNotNone(user)
        self.assertTrue(user.member)
        self.assertEquals(form_data['output'], user.signature)
        self.assertIn('Thanks for registering', response.data)

        db.session.delete(user)
        db.session.commit()
        
        # Test to verify redirection to wepay page when reg_and_pay is chosen.
        form_data['reg_and_pay'] = True
        response = self.client.post(url_for('users.register'), data=form_data)
        self.assertStatus(response, 302)
        self.assertIn('wepay.com', response.location)
        user = User.query.filter_by(email=form_data['email']).first()
        self.assertIsNotNone(user)
        self.assertIsNotNone(user.wepay_checkout_id)

        # Test trying to make an account with a duplicate email or netid.
        response = self.client.post(url_for('users.register'), data=form_data,
                                        follow_redirects=True)
        self.assert200(response)
        self.assertTemplateUsed('users/register.html')
        self.assertIn('already registered', response.data)

    def test_verify_membership_payment(self):
        """Tests verifiy_membership_payment modifies user properly."""
        from acm_phoenix.users import constants as USER
        with self.client.session_transaction() as sess:
            user = User("Test User", "testu001", "testu001@ucr.edu", "S", "CS",
                        "M", "test user", "testsig")
            db.session.add(user)
            db.session.commit()
            login_user(user)
            sess['user_id'] = user.id

        wepay_membership_response(current_user)

        # Bad key. Shouldn't modify user. Silently redirects to profile.
        response = self.client.get(url_for('users.verify_membership_payment',
                                           verification_key='randomkey'),
                                   follow_redirects=True)
        self.assert200(response)
        self.assertTemplateUsed('users/profile.html')
        self.assertEquals(current_user.membership_status, USER.IN_PROGRESS)
        self.assertIsNone(current_user.membership_paid_on)

        key = current_user.wepay_verification
        response = self.client.get(url_for('users.verify_membership_payment',
                                           verification_key=key),
                                   follow_redirects=True)
        self.assert200(response)
        self.assertTemplateUsed('users/profile.html')
        self.assertEquals(current_user.member_since,
                          current_user.membership_paid_on)

        self.assertEquals(user.membership_status, USER.PAID)

        logout_user()

    def test_payment_redirect(self):
        """Tests payment_redirect simulates payment part of registration."""
        with self.client.session_transaction() as sess:
            user = User("Test User", "testu001", "testu001@ucr.edu", "S", "CS",
                        "M", "test user", "testsig")
            db.session.add(user)
            db.session.commit()
            login_user(user)
            sess['user_id'] = user.id

        self.assertIsNone(current_user.wepay_checkout_id)
        response = self.client.get(url_for('users.payment_redirect'))
        self.assertStatus(response, 302)
        self.assertIn('wepay.com', response.location)
        self.assertIsNotNone(current_user.wepay_checkout_id)

    def test_authenticate_user(self):
        """Tests that calls to authenticate_user fail properly."""
        # Test redirects user to home if there is an error logging in.
        response = self.client.get(url_for('users.authenticate_user',
                                           error=True, code='randomcode'),
                                   follow_redirects=True)
        self.assert200(response)
        self.assertTemplateUsed('home.html')
        self.assertIn('There was an error authenticating you. Please again.',
                      response.data)

        try:
            # Test that flow code exchange fails because of bad code.
            response = self.client.get(url_for('users.authenticate_user',
                                               code='randomcode'))
        except FlowExchangeError:
            self.assert403(response)
        
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

    def test_view_profile(self):
        """Tests view_profile function with different netids."""
        with self.client.session_transaction() as sess:
            user = User("Test User", "testu001", "testu001@ucr.edu", "S", "CS",
                        "M", "test user", "testsig")
            db.session.add(user)
            db.session.commit()
            login_user(user)
            sess['user_id'] = user.id

            user = User("Test User", "testu002", "testu002@ucr.edu", "S", "CS",
                        "M", "test user", "testsig")
            db.session.add(user)
            db.session.commit()

        def append_netid_to_view_url(netid):
            return url_for('users.view_profile', user_netid=netid)

        # Test that if user views own profile, it shows the profile.html page.
        response = self.client.get(append_netid_to_view_url('testu001'))
        self.assert200(response)
        self.assertTemplateUsed('users/profile.html')
        self.assertContext('user', current_user)

        # Test that if user views another's profile, it shows view.html page.
        response = self.client.get(append_netid_to_view_url('testu002'))
        self.assert200(response)
        self.assertTemplateUsed('users/view.html')
        self.assertIn('testu002', response.data)

        # Test that if user asks for unknown user, they get an error message.
        response = self.client.get(append_netid_to_view_url('id'),
                                   follow_redirects=True)
        self.assert200(response)
        self.assertTemplateUsed('users/profile.html')
        self.assertIn('Sorry, we couldn&#39;t find the user you asked for.',
                      response.data)

        logout_user()
