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
