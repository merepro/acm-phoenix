from tests import ACMTestCase
from acm_phoenix import db
from acm_phoenix.users.models import User
from acm_phoenix.users import constants as USER
from datetime import datetime

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

    def test_create_user_with_ctor(self):
        """Test the constructor for the User Model."""
        user = User("Test User", "testu001", "testuser@ucr.edu", "S", "CS",
                    "M", "test user", "testsig")

        self.add_user(user)

        user = User.query.first()

        assert user.name == "Test User"
        assert user.email == "testuser@ucr.edu"
        assert user.netid == "testu001"
        assert user.standing == "S"
        assert user.major == "CS"
        assert user.shirt_size == "M"
        assert user.description == "test user"
        assert user.member is False
        assert user.membership_status is USER.IN_PROGRESS
        assert user.signature == "testsig"
        
        self.remove_user(user)

    def test_get_role(self):
        """Tests the user getRole function."""
        user = User()
        assert user.getRole() == 'user'

        user.role = USER.PUBLISHER
        assert user.getRole() == 'publisher'

        user.role = USER.ADMIN
        assert user.getRole() == 'admin'

    def test_get_member_status(self):
        """Tests the user getMemberStatus function."""
        user = User()
        assert user.getMemberStatus() == 'In Progress'

        user.membership_status = USER.UNREGISTERED
        assert user.getMemberStatus() == 'Unregistered'

        user.membership_status = USER.PAID
        assert user.getMemberStatus() == 'Official'

        user.membership_status = USER.UNPAID
        assert user.getMemberStatus() == 'Unrenewed'

    def test_role_predicates(self):
        """Test predicate functions that identify user roles."""
        user = User()
        assert user.isAdmin() is False and user.isPublisher() is False

        user.role = USER.PUBLISHER
        assert user.isPublisher() and not user.isAdmin()

        user.role = USER.ADMIN
        assert user.isPublisher() and user.isAdmin()
