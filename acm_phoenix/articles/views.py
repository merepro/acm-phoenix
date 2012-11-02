from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flaskext.markdown import Markdown
from flaskext.gravatar import Gravatar
from flask.ext.paginate import Pagination
from sqlalchemy import or_, and_

from acm_phoenix import app, db
from acm_phoenix.users.models import User
from acm_phoenix.articles.models import Post, Category, Tag
from acm_phoenix.articles.forms import SearchForm
from acm_phoenix.articles.constants import ORDER

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
    """
    A filter that formats a datetime as Month Day, Year.
    """
    format = '%b %d, %Y'
    return date.strftime(format)

@app.template_filter('format_authors')
def authors(author_ids):
    """
    Convert list of author ids into author names
    """
    if author_ids is None:
        return ''
    else:
        ids = []
        for author_id in author_ids.split(','):
            ids.append(User.id == int(author_id))
        authors = User.query.filter(or_(*ids)).all()
        if authors is None:
            return ''
        else:
            return 'by ' + ', '.join([author.name for author in authors])
        

@app.template_filter('format_query')
def formatted_query(query):
    """
    Pretty print query
    """
    stripped_query = query.replace('%', '') if query is not None else ''
    if len(stripped_query) == 0:
        return ""
    else:
        return "with query like '" + stripped_query + "'"

@app.template_filter('format_cats')
def formatted_category(cat_ids):
    """
    Convert list of category ids into category slugs
    """
    if cat_ids is None:
        return ''
    else:
        ids = []
        for cat_id in cat_ids.split(','):
            ids.append(Category.id == int(cat_id))
        cats = Category.query.filter(or_(*ids)).all()
        if cats is None:
            return ''
        else:
            return 'in ' + ', '.join([cat.slug.title() for cat in cats])

@app.template_filter('format_tags')
def formatted_tag(tag_ids):
    """
    Convert list of tag ids into tag names.
    """
    if tag_ids is None:
        return ''
    else:
        ids = []
        for tag_id in tag_ids.split(','):
            ids.append(Tag.id == int(tag_id))
        tags = Tag.query.filter(or_(*ids)).all()
        if tags is None:
            return ''
        else:
            return 'with tags: ' + ', '.join([tag.name.title() for tag in tags])

@app.template_filter('format_order')
def format_order(order):
    """
    Prints User-Friendly description of ORDERing technique.
    """
    if order is None:
        return ''
    else:
        return 'Ordered by ' + ORDER[order]

def valid_args(args):
    """
    Checks request args to see if they are valid. I.E., they contain a value.
    """
    return args is not None and len(args) > 0

def ilist_to_string(ilist):
    """
    Converts a list of Model IDs into strings to be sent as a request
    for searching.
    """
    return ','.join([str(i.id) for i in ilist])

# Routing rules
@mod.route('/', methods=['GET', 'POST'])
def show_all():
    """
    Display All articles by recency
    """

    # Request details
    req_cat = None
    req_auth = None
    req_tags = None
    search_term = None
    order = None

    # If there is no request, list posts by recency
    if len(request.args) == 0:
        posts = Post.query.order_by('created DESC').all()
    else:
        # Otherwise, get posts that fit requests
        search_term = "%" + (request.args.get('q') or "") + "%"


        categories = []
        req_cat = request.args.get('c')
        category_list = (req_cat.split(',')
                         if req_cat is not None 
                         else ([cat.id for cat in Category.query.all()]))
        
        for category in category_list:
            categories.append(Post.category_id == category)

        category_filter = or_(*categories)

        authors = []
        req_auth = request.args.get('a')
        author_list = (req_auth.split(',')
                       if req_auth is not None
                       else ([user.id for user in User.query.all()]))
        for author in author_list:
            authors.append(Post.author_id == author)

        author_filter = or_(*authors)

        # Generate list of tags to look for in relationship table.
        req_tags = request.args.get('t')
        tag_list = ([int(tag_id) for tag_id in req_tags.split(',')]
                    if req_tags is not None
                    else ([tag.id for tag in Tag.query.all()]))
        tags = Post.tags.any(Tag.id.in_(tag_list))

        order = request.args.get('order') or 'created DESC'

        """
        To be clear, this query looks for anything like the search term
        inside of the title or content of all posts and narrows it down
        to the selected authors, the selected categories, and the selected tags.
        """
        posts = Post.query.join(Category).join(User).filter(
            or_(Post.title.like(search_term),
                Post.gfm_content.like(search_term)),
            author_filter, category_filter,
            tags).order_by(order).all()

    form = SearchForm()
    if form.validate_on_submit():
        args = '?q=' + form.query.data
        if valid_args(form.category.data):
            args += '&c=' + ilist_to_string(form.category.data)
        if valid_args(form.author.data):
            args += '&a=' + ilist_to_string(form.author.data)
        if valid_args(form.tags.data):
            args += '&t=' + ilist_to_string(form.tags.data)
        args += '&order=' + form.order_by.data

        return redirect(url_for('articles.show_all') + args)

    page = int(request.args.get('page')) if request.args.get('page') else 1
    pagination = Pagination(posts, per_page=4, total=len(posts),
                            page=page)
    return render_template('articles/articles.html', posts=posts,
                           form=form, query=search_term, cats=req_cat,
                           authors=req_auth, tags=req_tags, order=order,
                           pagination=pagination)

@mod.route('/cat/<slug>/')
def show_cat(slug):
    """
    Show all posts under a certain category
    """
    cat = Category.query.filter_by(slug=slug).first()
    return redirect(url_for('articles.show_all') + '?c=' + str(cat.id))

@mod.route('/tag/<name>/')
def show_tag(name):
    """
    Show all posts under a certain tag name
    """
    tag = Tag.query.filter_by(name=name).first()
    return redirect(url_for('articles.show_all') + '?t=' + str(tag.id))

@mod.route('/author/<netid>/')
def show_author(netid):
    """
    Show all posts by a certain author. NetID is unique.
    """
    author = User.query.filter_by(netid=netid).first()
    return redirect(url_for('articles.show_all') + '?a=' + str(author.id))

@mod.route('/p/<slug>/')
def show_post(slug):
    """
    Show the full post on a seperate page.
    """
    post = Post.query.filter_by(slug=slug).first()
    return render_template('articles/post.html', post=post)
