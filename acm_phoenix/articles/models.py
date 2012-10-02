from flask import flash

from acm_phoenix import app, db
from acm_phoenix.users.models import User
from acm_phoenix.users.gfm import gfm

import re
from datetime import datetime

slug_re = re.compile('[a-zA-Z0-9]+')
def slugify(title):
    _title = title[:99].replace(' ', '-')  # Changed slug length to 100
    return '-'.join(re.findall(slug_re, _title))

class Category(db.Model):
    __tablename__ = 'articles_category'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    slug = db.Column(db.String)

    def __init__(self, title=None, slug=None):
        self.title = title
        self.slug = slug

    def __unicode__(self):
        return self.title

tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('articles_tag.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('articles_posts.id'))
)

class Tag(db.Model):
    __tablename__ = 'articles_tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))

    def __init__(self, tagname=None):
        self.name = tagname

    def __unicode__(self):
        return self.name

class Post(db.Model):
    __tablename__ = 'articles_posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    gfm_content = db.Column(db.String)
    created = db.Column(db.DateTime, default=datetime.utcnow())
    tags = db.relationship('Tag', secondary=tags,
                           primaryjoin=(id == tags.c.post_id),
                           secondaryjoin=(Tag.id == tags.c.tag_id),
                           backref=db.backref('tags', lazy='dynamic'))
    slug = db.Column(db.String)
    category_id = db.Column(db.Integer, db.ForeignKey('articles_category.id'))
    category = db.relationship('Category', primaryjoin=(category_id == Category.id),
                               backref=db.backref('cats', lazy='dynamic'), order_by=Category.slug)
    author_id = db.Column(db.Integer, db.ForeignKey('users_user.id'))
    author = db.relationship('User', primaryjoin=(author_id == User.id),
                             backref=db.backref('posters', lazy='dynamic'), order_by=User.name)

    def __unicode__(self):
        return self.slug
