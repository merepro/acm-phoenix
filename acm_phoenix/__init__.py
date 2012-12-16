from flask import Flask, render_template, g, session, url_for, redirect, request
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.paginate import Pagination

from time import strftime

db = None

# Define how to make configurable application
def create_app(config_object, debug=False):
    global db
    app = Flask(__name__)
    app.config.from_object(config_object)
    db = SQLAlchemy(app)

    return app

def register_blueprints(app):
    # Loading user modules.
    from acm_phoenix.users.views import mod as usersModule
    from acm_phoenix.articles.views import mod as articlesModule
    from acm_phoenix.snippets.views import mod as snippetsModule
    from acm_phoenix.admin import admin
    
    app.register_blueprint(usersModule)
    app.register_blueprint(articlesModule)
    app.register_blueprint(snippetsModule)
    admin.init_app(app)

app = create_app('config.DevelopmentConfig')
register_blueprints(app)

from acm_phoenix.users.models import User

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', error=error), 404

@app.before_request
def before_request():
    """
    pull user's profile from the database before every request are treated
    """
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@app.route('/')
def show_home():
    """
    Display home page to visitors and show front page articles.
    """
    from acm_phoenix.articles.forms import SearchForm
    from acm_phoenix.articles.models import Category, Post, Tag
    form = SearchForm()
    
    frontpage_filter = Post.query.filter(Tag.name == "frontpage")
    posts = frontpage_filter.order_by("created DESC").all()

    cats = Category.query.all()
    tags = Tag.query.all()

    author_filter = User.query.filter(User.role < 2)
    authors = author_filter.order_by("name ASC").all()

    page = int(request.args.get('page')) if request.args.get('page') else 1
    pagination = Pagination(posts, per_page=4, total=len(posts),
                            page=page)

    return render_template('home.html', posts=posts, form=form, 
                           pagination=pagination, tags=tags, cats=cats,
                           authors=authors)

@app.route('/logout')
def logout():
    """
    Removes user information from session
    """
    session.pop('user_id', None)
    return redirect(url_for('show_home'))
