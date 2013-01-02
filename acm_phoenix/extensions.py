# Global database instance.
from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# Global admin instance.
from flask.ext.admin import Admin
admin = Admin()

# Global login manager.
from flask.ext.login import LoginManager
login_manager = LoginManager()
