"""Tests for form creation and editing."""

from tests import ACMFormTest
from acm_phoenix.users.models import User
from acm_phoenix.users import constants as USER
from acm_phoenix.users.forms import RegisterForm, EditForm

import abc

class UserFormsTest(ACMFormTest):
    """Unit tests for User Forms."""
    forms = [RegisterForm, EditForm]

    def test_necessary_fields_in_form(self):
        reg_and_edit_fields = ['name', 'netid', 'email', 'standing', 'major',
                               'shirt_size', 'description']

        form = RegisterForm()
        assert self.fields_in_form_data(form.data, reg_and_edit_fields)

        form = EditForm()
        assert self.fields_in_form_data(form.data, reg_and_edit_fields)
        
        
    def test_required_fields_make_form_valid(self):
        """Tests that form is valid iff required fields are valid."""
        # Looping through the forms works here because they all have the same
        # fields.
        for formClass in self.forms:
            form = formClass(name='Test User', netid='testu001',
                             email='testu001@ucr.edu', standing='soph',
                             major='CS', shirt_size='S',
                             description='test user')
            assert form.validate()


        # Seeing if adding optional fields is really optional.
        for formClass in self.forms:
            form = formClass(name='Test User', netid='testu001',
                             email='testu001@ucr.edu', standing='soph',
                             major='CS', shirt_size='S')
            assert form.validate()

        # Making sure that leaving one required field empty fails validation.
        for formClass in self.forms:
            form = formClass(netid='testu001', email='testu001@ucr.edu',
                             standing='soph', major='CS', shirt_size='S')
            assert not form.validate()

    def test_forms_populate_models(self):
        """Tests that a validated form can populate associated model."""
        for formClass in self.forms:
            user = User()
            form = formClass(name='Test User', netid='testu001',
                             email='testu001@ucr.edu', standing='soph',
                             major='CS', shirt_size='S',
                             description='test user')
            form.populate_obj(user)
            assert user.name == 'Test User'
            assert user.netid == 'testu001'
            assert user.email == 'testu001@ucr.edu'
            assert user.standing == 'soph'
            assert user.major == 'CS'
            assert user.shirt_size == 'S'
            assert user.description == 'test user'
            assert user.role is USER.USER
            assert user.member is False
            assert user.membership_status is USER.IN_PROGRESS
            assert user.membership_paid_on is None
            assert user.wepay_verification is None
            assert user.wepay_checkout_id is None
            assert user.signature is None

