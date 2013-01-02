"""Database Models used by users and other modules"""

from flask.ext.login import UserMixin
from acm_phoenix.extensions import db
from acm_phoenix.users import constants as USER
from datetime import datetime

class User(db.Model, UserMixin):
    """
    Defines the User object.
    """
    __tablename__ = 'users_user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    netid = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(120), unique=True)
    role = db.Column(db.SmallInteger, default=USER.USER)
    member = db.Column(db.Boolean, default=False)
    member_since = db.Column(db.DateTime)
    membership_status = db.Column(db.SmallInteger, default=USER.UNREGISTERED)
    membership_paid_on = db.Column(db.DateTime)
    description = db.Column(db.Text)
    standing = db.Column(db.String(15))
    major = db.Column(db.String(50))
    shirt_size = db.Column(db.String(5))
    wepay_verification = db.Column(db.String(255))
    wepay_checkout_id = db.Column(db.Integer)
    signature = db.Column(db.LargeBinary)

    def __init__(self, name=None, netid=None, email=None, standing=None,
                 major=None, shirt_size=None, description=None,
                 signature=None):
        self.name = name
        self.email = email
        self.netid = netid
        self.standing = standing
        self.major = major
        self.shirt_size = shirt_size
        self.description = description
        self.member = False
        self.member_since = datetime.now()
        self.membership_status = USER.IN_PROGRESS
        self.role = USER.USER
        self.signature = signature

    def getRole(self):
        """
        Get this user's role as a string.
        """
        return USER.ROLE[self.role]

    def getMemberStatus(self):
        """
        Get this user's membership status as a string.
        """
        return USER.MEMBER_STATUS[self.membership_status]

    def __repr__ (self):
        """
        Represent User as Name (email)
        """
        return '%s (%s)' % (self.name, self.email)

    def __unicode__(self):
        """
        Only full name for unicode representation
        """
        return self.name

    def isAdmin(self):
        """
        True if User is an administrator
        """
        return self.role == USER.ADMIN

    def isPublisher(self):
        """
        True if User is at least a publisher
        """
        return self.role <= USER.PUBLISHER
