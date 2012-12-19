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
        self.assertIsNone(user)

    def test_add_user_to_db(self):
        """Tests that users can be added to the database."""
        user = User()
        self.add_user(user)

        self.assertIn(user, db.session)
        self.remove_user(user)

    def test_remove_user_from_db(self):
        """Tests that users can be removed from the database."""
        self.add_user()

        user = User.query.first()
        self.remove_user(user)
        self.assertNotIn(user, db.session)

    def test_default_user_values(self):
        """Tests that the values for a default User are as expected."""
        now = datetime.now()
        self.add_user()
        user = User.query.first()

        self.assertIsNone(user.name)
        self.assertIsNone(user.netid)
        self.assertIsNone(user.email)
        self.assertIs(user.role, USER.USER)
        self.assertFalse(user.member)
        self.assertGreaterEqual(user.member_since, now)
        self.assertIs(user.membership_status, USER.IN_PROGRESS)
        self.assertIsNone(user.membership_paid_on)
        self.assertIsNone(user.description)
        self.assertIsNone(user.standing)
        self.assertIsNone(user.major)
        self.assertIsNone(user.shirt_size)
        self.assertIsNone(user.wepay_verification)
        self.assertIsNone(user.wepay_checkout_id)
        self.assertIsNone(user.signature)

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

        self.assertEquals(user.name, "Test User")
        self.assertEquals(user.email, "testuser@ucr.edu")
        self.assertEquals(user.netid, "testu001")
        self.assertEquals(user.standing, "S")
        self.assertEquals(user.major, "CS")
        self.assertEquals(user.shirt_size, "M")
        self.assertEquals(user.description, "test user")
        self.assertTrue(user.member)
        self.assertIs(user.membership_status, USER.USER)
        self.assertEquals(user.signature, "testsig")

        self.remove_user(user)

    def test_create_user_with_ctor(self):
        """Test the constructor for the User Model."""
        user = User("Test User", "testu001", "testuser@ucr.edu", "S", "CS",
                    "M", "test user", "testsig")

        self.add_user(user)

        user = User.query.first()

        self.assertEquals(user.name, "Test User")
        self.assertEquals(user.email, "testuser@ucr.edu")
        self.assertEquals(user.netid, "testu001")
        self.assertEquals(user.standing, "S")
        self.assertEquals(user.major, "CS")
        self.assertEquals(user.shirt_size, "M")
        self.assertEquals(user.description, "test user")
        self.assertFalse(user.member)
        self.assertIs(user.membership_status, USER.IN_PROGRESS)
        self.assertEquals(user.signature, "testsig")
        
        self.remove_user(user)

    def test_get_role(self):
        """Tests the user getRole function."""
        user = User()
        self.assertEquals(user.getRole(), 'user')

        user.role = USER.PUBLISHER
        self.assertEquals(user.getRole(), 'publisher')

        user.role = USER.ADMIN
        self.assertEquals(user.getRole(), 'admin')

    def test_get_member_status(self):
        """Tests the user getMemberStatus function."""
        user = User()
        self.assertEquals(user.getMemberStatus(), 'In Progress')

        user.membership_status = USER.UNREGISTERED
        self.assertEquals(user.getMemberStatus(), 'Unregistered')

        user.membership_status = USER.PAID
        self.assertEquals(user.getMemberStatus(), 'Official')

        user.membership_status = USER.UNPAID
        self.assertEquals(user.getMemberStatus(), 'Unrenewed')

    def test_role_predicates(self):
        """Test predicate functions that identify user roles."""
        user = User()
        self.assertFalse(user.isAdmin())
        self.assertFalse(user.isPublisher())

        user.role = USER.PUBLISHER
        self.assertTrue(user.isPublisher())
        self.assertFalse(user.isAdmin())

        user.role = USER.ADMIN
        self.assertTrue(user.isPublisher())
        self.assertTrue(user.isAdmin())
