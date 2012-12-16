from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.testing import TestCase
from acm_phoenix import db, create_app, register_blueprints
from acm_phoenix.users.models import User
from acm_phoenix.users import constants as USER
from datetime import datetime

# Unit tests for user interactions with system
class UserModelTest(TestCase):
    app = None

    def create_app(self):
        self.app = create_app('config.TestingConfig')
        #register_blueprints(self.app)
        return self.app

    def remove_user(self, user):
        db.session.delete(user)
        db.session.commit()

    def add_user(self, user=None):
        if user is None:
            user = User()
        db.session.add(user)
        db.session.commit()

    def test_no_default_users(self):
        user = User.query.first()
        assert user is None

    def test_add_user_to_db(self):
        user = User()
        self.add_user(user)

        assert user in db.session
        self.remove_user(user)

    def test_remove_user_from_db(self):
        self.add_user()

        user = User.query.first()
        self.remove_user(user)
        assert user not in db.session

    def test_default_user_values(self):
        now = datetime.now()
        self.add_user()
        user = User.query.first()

        assert user.name is None
        assert user.netid is None
        assert user.email is None
        assert user.role is USER.USER
        assert user.member is False
        assert user.member_since >= now
        assert user.membership_status is USER.IN_PROGRESS
        assert user.membership_paid_on is None
        assert user.description is None
        assert user.standing is None
        assert user.major is None
        assert user.shirt_size is None
        assert user.wepay_verification is None
        assert user.wepay_checkout_id is None
        assert user.signature is None

        self.remove_user(user)

    def test_modify_user_from_db(self):
        self.add_user()
        user = User.query.first()

        user.name = "Test User"
        user.email = "testuser@ucr.edu"
        user.netid = "testu001"
        user.standing = "S"
        user.major = "CS"
        user.shirt_size = "M"
        user.description = "test user"
        user.member = True
        user.membership_status = USER.USER
        user.signature = "testsig"

        self.add_user(user)
        user = User.query.first()

        assert user.name == "Test User"
        assert user.email == "testuser@ucr.edu"
        assert user.netid == "testu001"
        assert user.standing == "S"
        assert user.major == "CS"
        assert user.shirt_size == "M"
        assert user.description == "test user"
        assert user.member is True
        assert user.membership_status is USER.USER
        assert user.signature == "testsig"

        self.remove_user(user)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
