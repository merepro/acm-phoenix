"""Forms that will be used with the Articles models"""

from flask.ext.wtf import (Form, TextField, SelectField, SubmitField, 
                           QuerySelectMultipleField)

from acm_phoenix.users.models import User
from acm_phoenix.articles.models import Category, Tag

def all_cats():
    """
    Get all categories.
    """
    return Category.query.all()

def all_publishers():
    """
    Get all users with at least a publisher role.
    """
    return User.query.filter(User.role <= 1).order_by('name').all()

def all_tags():
    """
    Get all tags in alphabetical order.
    """
    return Tag.query.order_by('name').all()

class SearchForm(Form):
    """
    Form used to help Users find articles.
    """
    query = TextField(u'Search Query')
    category = QuerySelectMultipleField(u'In Category', query_factory=all_cats)
    author = QuerySelectMultipleField(u'Authored By',
                                      query_factory=all_publishers)
    tags = QuerySelectMultipleField(u'With Tags', query_factory=all_tags)

    order_by = SelectField(u'Order by', default='created',
                           choices=[('created%20DESC', 'Recency'),
                                    ('title', 'Title'),
                                    ('articles_category.slug', 'Category Name'),
                                    ('users_user.name', 'Author Name')]
                           )
