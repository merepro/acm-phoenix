from flask import Flask
from acm_phoenix.extensions import db, admin

def create_app(config_object, debug=False):
    """Creates a valid acm_phoenix application."""
    app = Flask(__name__)
    app.config.from_object(config_object)
    db.init_app(app)
    register_blueprints(app)
    register_filters(app)
    register_login_manager(app)

    return app

def register_blueprints(app):
    """Registers submodules as blueprints."""
    from acm_phoenix.views import mod as indexModule
    from acm_phoenix.users.views import mod as usersModule
    from acm_phoenix.articles.views import mod as articlesModule
    from acm_phoenix.snippets.views import mod as snippetsModule
    
    app.register_blueprint(indexModule)
    app.register_blueprint(usersModule)
    app.register_blueprint(articlesModule)
    app.register_blueprint(snippetsModule)
    register_admin_backend(app)

def register_admin_backend(app):
    from flask.ext.admin import Admin
    from acm_phoenix.admin.models import (AdminView, UserAdmin, ReportAdmin,
                                          PostAdmin, CategoryAdmin, TagAdmin)

    # User Admin Views
    admin = Admin(index_view=AdminView())
    admin.add_view(UserAdmin(db.session))
    admin.add_view(ReportAdmin(db.session))
    admin.add_view(PostAdmin(db.session))
    admin.add_view(CategoryAdmin(db.session))
    admin.add_view(TagAdmin(db.session))
    admin.init_app(app)

def register_login_manager(app):
    from acm_phoenix.extensions import login_manager
    from acm_phoenix.users.models import User

    login_manager.login_view = 'users.login'
    login_manager.refresh_view = 'users.login'
    login_manager.login_message = ''

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
    login_manager.setup_app(app)

def register_filters(app):
    """Initializes all filters needed for submodules."""
    from flask.ext.gravatar import Gravatar
    from flask.ext.markdown import Markdown

    Gravatar(app)
    Markdown(app)

    @app.template_filter('formatted_time')
    def timesince(date):
        """A filter that formats a datetime as Month Day, Year."""
        format = '%b %d, %Y'
        return date.strftime(format)

    @app.template_filter('format_authors')
    def authors(author_ids):
        """Convert list of author ids into author names."""
        from sqlalchemy import or_
        from acm_phoenix.users.models import User
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
        """Pretty print query."""
        stripped_query = query.replace('%', '') if query is not None else ''
        if len(stripped_query) == 0:
            return ''
        else:
            return "with query like '" + stripped_query + "'"

    @app.template_filter('format_cats')
    def formatted_category(cat_ids):
        """Convert list of category ids into category slugs."""
        from sqlalchemy import or_
        from acm_phoenix.articles.models import Category
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
        """Convert list of tag ids into tag names."""
        from sqlalchemy import or_
        from acm_phoenix.articles.models import Tag
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
                return ('with tags: ' + 
                        ', '.join([tag.name.title() for tag in tags]))

    @app.template_filter('format_order')
    def format_order(order):
        """Prints User-Friendly description of ordering preference."""
        from acm_phoenix.articles.constants import ORDER
        if order is None:
            return ''
        else:
            return 'Ordered by ' + ORDER[order]
