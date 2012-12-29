"""Tests for form creation and editing."""

from tests import ACMFormTest
from acm_phoenix.users.models import User
from acm_phoenix.users import constants as USER
from acm_phoenix.users.forms import RegisterForm, EditForm
from flask.ext.wtf import (TextField, SelectField, 
                           TextAreaField)

class UserFormsTest(ACMFormTest):
    """Unit tests for User Forms."""
    __test__ = True
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

    def test_fields_have_expected_types(self):
        """Tests that each field has expected Field type."""
        for formClass in self.forms:
            form = formClass()
            self.assertType(form, 'name', TextField)
            self.assertType(form, 'netid', TextField)
            self.assertType(form, 'email', TextField)
            self.assertType(form, 'standing', SelectField)
            self.assertType(form, 'major', SelectField)
            self.assertType(form, 'shirt_size', SelectField)
            self.assertType(form, 'description', TextAreaField)

    def test_select_fields_have_expected_choices(self):
        """Tests that each SelectField in the form has the expected choices."""
        standing_choices = [('freshman', 'Freshman'),
                            ('soph', 'Sophomore'),
                            ('junior', 'Junior'),
                            ('senior', 'Senior'),
                            ('alum', 'Alumni'),
                            ('grad', 'Graduate Student'),
                            ('faculty', 'Faculty')]
        
        major_choices = [('CS', 'CS (Computer Science)'),
                         ('CE', 'CE (Computer Engineering)'),
                         ('BI', 'BI (Business Informatics)'),
                         ('Other', 'Other')]

        shirt_size_choices = [('S', 'Small'),
                              ('M', 'Medium'),
                              ('L', 'Large'),
                              ('XL', 'X-Large'),
                              ('XXL', '2X-Large')]

        for formClass in self.forms:
            form = formClass()
            self.assertChoices(form, 'standing', standing_choices)
            self.assertChoiceValues(form, 'standing', standing_choices)
            self.assertChoices(form, 'major', major_choices)
            self.assertChoiceValues(form, 'major', major_choices)
            self.assertChoices(form, 'shirt_size', shirt_size_choices)
            self.assertChoiceValues(form, 'shirt_size', shirt_size_choices)
            

    def test_fields_have_expected_validators(self):
        """Tests that form fields have the expected validators."""
        for formClass in self.forms:
            form = formClass()
            self.assertRequired(form, 'name')
            self.assertRequired(form, 'netid')
            self.assertRequired(form, 'email')
            self.assertEmail(form, 'email')
            self.assertRequired(form, 'standing')
            self.assertRequired(form, 'major')
            self.assertRequired(form, 'shirt_size')
            self.assertOptional(form, 'description')
            
        
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

