from flask import Flask, render_template, g
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

@app.route('/')
def show_home():
    return render_template('home.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

from acm_phoenix.users.views import mod as usersModule
app.register_blueprint(usersModule)
