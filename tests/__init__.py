from flask.ext.testing import TestCase
from flask.ext.wtf import Field, Required, Email, Optional
from acm_phoenix import db, create_app, register_blueprints

import abc

class ACMTestCase(TestCase):
    """Test case wrapper that implements common initialization code"""    
    app = None
    client = None

    def create_app(self):
        """Creates testing application with correct database configuration"""
        self.app = create_app('config.TestingConfig')
        self.client = self.app.test_client()
        return self.app

    def setUp(self):
        """Creates database 'test.db' and loads models"""
        db.create_all()

    def tearDown(self):
        """Destroys session and drops all tables"""
        db.session.remove()
        db.drop_all()

class ACMFormTest(ACMTestCase):
    # Derived form tests should define the forms to be tested in this list.
    forms = []

    def _get_field(self, form, field_name):
        """Gets the field attribute of field_name from a given form."""
        return getattr(form, field_name)

    def _get_validator(self, field, validator_class):
        """Gets a particular validator_class from a field."""
        for validator in field.validators:
            if isinstance(validator, validator_class):
                return validator
        return None

    def get_validator(self, form, field_name, validator_class):
        """Gets a particular validator_class from form.field_name."""
        return self._get_validator(
            self._get_field(form, field_name),
            validator_class)

    def has_field(self, form, field_name):
        return hasattr(form, field_name)

    def fields_in_form(self, form, fields):
        """Returns true if all fields are in form_data."""
        for field_name in fields:
            if not self.has_field(form, field_name):
                return False
        return True

    def assertType(self, form, field_name, field_type):
        """Asserts field_name has field_type in form."""
        self.assertTrue(self.has_field(form, field_name))
        self.assertIs(self._get_field(field_name).__class__, field_type)

    def assertOptional(self, form, field_name):
        """Asserts field_name is an optional field in form."""
        self.assertIsNotNone(self.get_validator(form, field_name, Optional))

    def assertRequired(self, form, field_name):
        """Asserts field_name is a required field in form."""
        self.assertIsNotNone(self.get_validator(form, field_name, Required))

    def assertEmail(self, form, field_name):
        """Asserts field_name is an email field in form."""
        self.assertIsNotNone(self.get_validator(form, field_name, Email))

    @abc.abstractmethod
    def test_necessary_fields_in_form(self):
        """Tests that necessary fields are in forms to be tested."""
        return


    @abc.abstractmethod
    def test_fields_have_expected_validators(self):
        """Tests that form fields have the expected validators."""
        return

    @abc.abstractmethod
    def test_required_fields_make_form_valid(self):
        """Tests that form is valid iff required fields are valid."""
        return

    @abc.abstractmethod
    def test_forms_populate_models(self):
        """Tests that a validated form can populate associated model."""
        return

    def test_forms_have_csrf_disabled(self):
        """Tests that any form being tested has csrf disabled.

        Without having csrf tokens disabled, it is impossible to test form
        submissions by post because WTForms uses CSRF tokens. WTForms should
        decide whether or not to turn CSRF tokens off by the test configuration,
        but we want to make sure."""
        for formClass in self.forms:
            form = formClass()
            self.assertFalse(form.csrf_enabled)

    def test_create_form_from_ctor(self):
        """Tests that a valid form can be made from the construtor."""
        for formClass in self.forms:
            form = formClass()
            self.assertIsNotNone(form)

    def test_empty_form_validation(self):
        """Tests that empty forms are invalid."""
        for formClass in self.forms:
            form = formClass()
            self.assertFalse(form.validate())
        
