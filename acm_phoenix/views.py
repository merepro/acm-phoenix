from flask import (Blueprint, render_template, session, url_for, redirect,
                   request)
from flask.ext.login import login_required, logout_user
from flask.ext.paginate import Pagination

from time import strftime

from acm_phoenix.users.models import User

mod = Blueprint('index', __name__, url_prefix='')

@mod.errorhandler(404)
def not_found(error):
    return render_template('404.html', error=error), 404

@mod.route('/')
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
                            page=page, link_size='large')

    return render_template('home.html', posts=posts, form=form, 
                           pagination=pagination, tags=tags, cats=cats,
                           authors=authors)

@mod.route('/logout')
@login_required
def logout():
    """
    Removes user information from session
    """
    logout_user()
    return redirect(url_for('index.show_home'))
