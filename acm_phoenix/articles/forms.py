from flask.ext.wtf import Form, TextField, SelectField, SubmitField, QuerySelectMultipleField

from acm_phoenix.users.models import User
from acm_phoenix.articles.models import Category, Tag

def all_cats():
    return Category.query.all()

def all_publishers():
    return User.query.filter(User.role <= 1).order_by('name').all()

def all_tags():
    return Tag.query.order_by('name').all()

class SearchForm(Form):
    query = TextField(u'Search Query')
    category = QuerySelectMultipleField(u'In Category', query_factory=all_cats)
    author = QuerySelectMultipleField(u'Authored By', query_factory=all_publishers)
    tags = QuerySelectMultipleField(u'With Tags', query_factory=all_tags)

    # TODO(paranoiacblack): Sort by Author Name
    order_by = SelectField(u'Order by', default='created',
                           choices=[('created', 'Recency'), ('title', 'Title'), ('slug', 'Category Name'), ('author', 'Author Name')])
