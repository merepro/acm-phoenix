from flask import Flask, render_template, g, session, url_for, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqlamodel import ModelView

from time import strftime

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

from acm_phoenix.users.views import mod as usersModule
app.register_blueprint(usersModule)

from acm_phoenix.users.models import User
from acm_phoenix.admin.models import UserAdmin, ReportAdmin

# Admin Views
admin = Admin(app)
admin.add_view(UserAdmin(db.session))
admin.add_view(ReportAdmin(db.session))

@app.before_request
def before_request():
  """
  pull user's profile from the database before every request are treated
  """
  g.user = None
  if 'user_id' in session:
    g.user = User.query.get(session['user_id']);


@app.route('/')
def show_home():
    """
    Display home page to visitors
    """
    return render_template('home.html')

@app.route('/logout')
def logout():
    """
    Removes user information from session
    """
    session.pop('user_id', None)
    return redirect(url_for('show_home'))
