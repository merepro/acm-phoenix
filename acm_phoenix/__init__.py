from flask import Flask, render_template, g, session, url_for, redirect, request
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin import Admin
from flask.ext.paginate import Pagination

from time import strftime

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', error=error), 404

# Loading user modules.
from acm_phoenix.users.views import mod as usersModule
app.register_blueprint(usersModule)

from acm_phoenix.articles.views import mod as articlesModule
app.register_blueprint(articlesModule)

from acm_phoenix.snippets.views import mod as snippetsModule
app.register_blueprint(snippetsModule)

from acm_phoenix.users.models import User
from acm_phoenix.admin.models import (AdminView, UserAdmin, ReportAdmin, 
                                      PostAdmin, CategoryAdmin, TagAdmin)
from acm_phoenix.articles.models import Post, Tag
from acm_phoenix.articles.forms import SearchForm

# User Admin Views
admin = Admin(index_view=AdminView())
admin.add_view(UserAdmin(db.session))
admin.add_view(ReportAdmin(db.session))
admin.add_view(PostAdmin(db.session))
admin.add_view(CategoryAdmin(db.session))
admin.add_view(TagAdmin(db.session))
admin.init_app(app)

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
    form = SearchForm()
    frontpage_filter = Post.query.filter(Tag.name == "frontpage")
    posts = frontpage_filter.order_by("created DESC").all()
    page = int(request.args.get('page')) if request.args.get('page') else 1
    pagination = Pagination(posts, per_page=4, total=len(posts),
                            page=page)
    return render_template('home.html', posts=posts, form=form, 
                           pagination=pagination)

@app.route('/logout')
def logout():
    """
    Removes user information from session
    """
    session.pop('user_id', None)
    return redirect(url_for('show_home'))
