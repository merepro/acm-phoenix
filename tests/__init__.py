from flask.ext.testing import TestCase
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

    def fields_in_form_data(self, form_data, fields):
        for field in fields:
            if field not in form_data:
                return False
        return True

    @abc.abstractmethod
    def test_necessary_fields_in_form(self):
        """Tests that necessary fields are in forms to be tested."""
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
        for formClass in self.forms:
            """Tests that empty forms are invalid."""
            form = formClass()
            self.assertFalse(form.validate())
        
