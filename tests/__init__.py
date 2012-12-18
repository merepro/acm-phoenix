from flask.ext.testing import TestCase
from acm_phoenix import db, create_app, register_blueprints

class ACMTestCase(TestCase):
    """Test case wrapper that implements common initialization code"""    
    app = None

    def create_app(self):
        """Creates testing application with correct database configuration"""
        self.app = create_app('config.TestingConfig')
        #register_blueprints(self.app)
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

    def test_forms_have_csrf_disabled(self):
        """Tests the any form being tested has csrf disabled.

        Without having csrf tokens disabled, it is impossible to test form
        submissions by post because WTForms uses CSRF tokens. WTForms should
        decide whether or not to turn CSRF tokens off by the test configuration,
        but we want to make sure."""
        for formClass in self.forms:
            form = formClass()
            assert form.csrf_enabled is False

    def test_create_form_from_ctor(self):
        """Tests that a valid form can be made from the construtor."""
        for formClass in self.forms:
            form = formClass()
            assert form is not None
