from flask.ext.wtf import Form, TextField, SelectField, SubmitField, SelectMultipleField

from acm_phoenix.users.models import User
from acm_phoenix.articles.models import Category, Tag

class SearchForm(Form):
    query = TextField(u'Search Query')
    category = SelectMultipleField(u'In Category', coerce=int,
                                   choices=[(c.id, c.slug.title()) for c in Category.query.order_by('slug').all()])
    author = SelectMultipleField(u'Authored By', coerce=int,
                                 choices=[(a.id, a.name.title()) for a in User.query.filter(User.role <= 1).order_by('name').all()])
    tags = SelectMultipleField(u'With Tags', coerce=int,
                               choices=[(t.id, t.name.title()) for t in Tag.query.order_by('name').all()])

    # TODO(paranoiacblack): Sort by Author Name
    order_by = SelectField(u'Order by', default='created',
                           choices=[('created', 'Recency'), ('title', 'Title'), ('slug', 'Category Name'), ('author', 'Author Name')])
