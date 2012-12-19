"""Tests for form creation and editing."""

from tests import ACMFormTest
from acm_phoenix.users.models import User
from acm_phoenix.users import constants as USER
from acm_phoenix.users.forms import RegisterForm, EditForm

import abc

class UserFormsTest(ACMFormTest):
    """Unit tests for User Forms."""
    forms = [RegisterForm, EditForm]

    # Looping through the forms works here because RegisterForm and EditForm
    # have the same fields.

    def test_necessary_fields_in_form(self):
        """Tests that necessary fields are in forms to be tested."""
        reg_and_edit_fields = ['name', 'netid', 'email', 'standing', 'major',
                               'shirt_size', 'description']

        for formClass in self.forms:
            form = formClass()
            self.assertTrue(self.fields_in_form(form, reg_and_edit_fields))
        
        
    def test_required_fields_make_form_valid(self):
        """Tests that form is valid iff required fields are valid."""
        for formClass in self.forms:
            form = formClass(name='Test User', netid='testu001',
                             email='testu001@ucr.edu', standing='soph',
                             major='CS', shirt_size='S',
                             description='test user')
            self.assertTrue(form.validate())


        # Seeing if adding optional fields is really optional.
        for formClass in self.forms:
            form = formClass(name='Test User', netid='testu001',
                             email='testu001@ucr.edu', standing='soph',
                             major='CS', shirt_size='S')
            self.assertTrue(form.validate())

        # Making sure that leaving one required field empty fails validation.
        for formClass in self.forms:
            form = formClass(netid='testu001', email='testu001@ucr.edu',
                             standing='soph', major='CS', shirt_size='S')
            self.assertFalse(form.validate())

    def test_forms_populate_models(self):
        """Tests that a validated form can populate associated model."""
        for formClass in self.forms:
            user = User()
            form = formClass(name='Test User', netid='testu001',
                             email='testu001@ucr.edu', standing='soph',
                             major='CS', shirt_size='S',
                             description='test user')
            form.populate_obj(user)
            self.assertEquals(user.name, 'Test User')
            self.assertEquals(user.netid, 'testu001')
            self.assertEquals(user.email, 'testu001@ucr.edu')
            self.assertEquals(user.standing, 'soph')
            self.assertEquals(user.major, 'CS')
            self.assertEquals(user.shirt_size, 'S')
            self.assertEquals(user.description, 'test user')
            self.assertIs(user.role, USER.USER)
            self.assertFalse(user.member)
            self.assertIs(user.membership_status, USER.IN_PROGRESS)
            self.assertIsNone(user.membership_paid_on)
            self.assertIsNone(user.wepay_verification)
            self.assertIsNone(user.wepay_checkout_id)
            self.assertIsNone(user.signature)

