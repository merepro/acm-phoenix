from acm_phoenix import db
from acm_phoenix.users import constants as USER

class User(db.Model):
    __tablename__ = 'users_user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True)
    role = db.Column(db.SmallInteger, default=USER.USER)
    member = db.Column(db.Boolean, default=False)
    membership_paid_on = db.Column(db.DateTime)
    description = db.Column(db.Text)

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def getRole(self):
        return USER.ROLE[self.role]

    def __repr__ (self):
        return '%s (%s)' % (self.name, self.email)
