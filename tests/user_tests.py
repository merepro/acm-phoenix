from tests import ACMTestCase
from acm_phoenix import db
from acm_phoenix.users.models import User
from acm_phoenix.users import constants as USER
from datetime import datetime

# Unit tests for user interactions with system
class UserModelTest(ACMTestCase):
    """Unit tests for the User SQL Model."""
    # Helper functions for testing database interactions
    def remove_user(self, user):
        """Removes a specific user from the database."""
        db.session.delete(user)
        db.session.commit()

    def add_user(self, user=None):
        """Adds a user to the database.

        user is optional, so if no user is passed in, the default User object
        will be used instead."""
        if user is None:
            user = User()
        db.session.add(user)
        db.session.commit()

    def test_no_default_users(self):
        """Tests that there are no default users in the database."""
        user = User.query.first()
        assert user is None

    def test_add_user_to_db(self):
        """Tests that users can be added to the database."""
        user = User()
        self.add_user(user)

        assert user in db.session
        self.remove_user(user)

    def test_remove_user_from_db(self):
        """Tests that users can be removed from the database."""
        self.add_user()

        user = User.query.first()
        self.remove_user(user)
        assert user not in db.session

    def test_default_user_values(self):
        """Tests that the values for a default User are as expected."""
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
        """Tests that a User Object can be modified and recommitted."""
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
