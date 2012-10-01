from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flaskext.markdown import Markdown
from flaskext.gravatar import Gravatar
from sqlalchemy import or_, and_

from acm_phoenix import app, db
from acm_phoenix.users.models import User
from acm_phoenix.articles.models import Post, Category, Tag
from acm_phoenix.articles.forms import SearchForm

# Python implementation of Github Flavored Markdown
from acm_phoenix.users.gfm import gfm

# Article Blueprint
mod = Blueprint('articles', __name__, url_prefix='/articles')

# Initialize Markdown
Markdown(app)

gravatar = Gravatar(app,
                    size=50,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False)

@app.template_filter('formatted_time')
def timesince(date):
    format = "%b %d, %Y"
    return date.strftime(format)

def valid_args(args):
    return args is not None and len(args) > 0

def ilist_to_string(ilist):
    return "".join([str(i) for i in ilist])

# Routing rules
@mod.route('/', methods=['GET', 'POST'])
def show_all():
    """
    Display All articles by recency
    """

    # Request details
    req_cats = None
    req_auth = None
    req_tags = None

    # If there is no request, list posts by recency
    if len(request.args) == 0:
        posts = Post.query.order_by('created DESC').all()
    else:
        # Otherwise, get posts that fit requests
        search_term = "%" + (request.args.get('q') or "") + "%"

        # Create filtering conditions
        filters = []

        categories = []
        req_cat = request.args.get('c')
        category_list = req_cat.split(',') if req_cat is not None else ([cat.id for cat in Category.query.all()])
        for category in category_list:
            categories.append(Post.category_id == category)

        filters.append(or_(*categories))

        authors = []
        req_auth = request.args.get('a')
        author_list = req_auth.split(',') if req_auth is not None else ([user.id for user in User.query.all()])
        for author in author_list:
            authors.append(Post.author_id == author)

        filters.append(and_(*authors))

        # Generate list of tags to look for in relationship table.
        req_tags = request.args.get('t')
        tag_list = [int(tag_id) for tag_id in req_tags.split(',')] if req_tags is not None else ([tag.id for tag in Tag.query.all()])
        tags = Post.tags.any(Tag.id.in_(tag_list))

        order = request.args.get('order') or "created"

        """
        To be clear, this query looks for anything like the search term
        inside of the title or content of all posts and narrows it down
        to the selected authors and categories and narrows that down
        by the selected tags.
        """
        posts = Post.query.filter(or_(Post.title.like(search_term),
                                      Post.gfm_content.like(search_term)),
                                  or_(*filters), tags).order_by(order).all()

    form = SearchForm()
    if form.validate_on_submit():
        args = "?q=" + form.query.data
        if valid_args(form.category.data):
            args += "&c=" + ilist_to_string(form.category.data)
        if valid_args(form.author.data):
            args += "&a=" + ilist_to_string(form.author.data)
        if valid_args(form.tags.data):
            args += "&t=" + ilist_to_string(form.tags.data)
        args += "&order=" + form.order_by.data

        return redirect(url_for('articles.show_all') + args)
    return render_template('articles/articles.html', posts=posts, form=form, cats=req_cats, authors=req_auth, tags=req_tags)

@mod.route('/cat/<slug>/')
def show_cat(slug):
    """
    Show all posts under a certain category
    """
    cat = Category.query.filter_by(slug=slug).first()
    return redirect(url_for('articles.show_all') + '?c=' + str(cat.id))
