from flask import render_template, send_file, g, redirect, url_for
from flask.ext.admin.contrib.sqlamodel import ModelView
from flask.ext.admin import expose
from flask.ext.admin.base import AdminIndexView
from flask.ext.admin.actions import action
from flask.ext.admin.babel import gettext, lazy_gettext

from acm_phoenix import app
from acm_phoenix.users.models import User
from acm_phoenix.users import constants as USER
from acm_phoenix.users.decorators import requires_login

from acm_phoenix.articles.models import Post, Tag, Category

from wtforms.fields import SelectField, TextAreaField

# For Rendering PDF and writing to Zipfiles
import xhtml2pdf.pisa as pisa
import cStringIO as StringIO
import zipfile

from time import strftime

class AdminView(AdminIndexView):
    """
    A subclass of the AdminIndexView that forces user authentication. The main viewport for user Administration.
    """
    @expose('/')
    def index(self):
        return self.render('admin/master.html')

    def is_accessible(self):
        # Only accessible to those with at least a publisher role.
        return g.user is not None and g.user.isPublisher()


class UserAdmin(ModelView):
    """
    A modification on ModelView that removes extraneous columns like Description,
    WePay Verification Key, and Signature
    """
    excluded_list_columns = ['description', 'wepay_verification', 'signature', 'wepay_checkout_id']

    # Only text based columns are searchable anyways.
    searchable_columns = (User.name, User.email, User.netid, User.standing, User.major)

    list_formatters = dict(role=lambda m, p: USER.ROLE[m.role].title(),
                           membership_status=lambda m, p: USER.MEMBER_STATUS[m.membership_status].title(),
                           member_since=lambda m, p: m.member_since.strftime("%b %d, %Y"),
                           membership_paid_on=lambda m, p: m.membership_paid_on.strftime("%b %d, %Y") if m.membership_paid_on is not None else "Not Paid",
                           standing=lambda m, p: m.standing.title())

    # Some impossible page size
    page_size = 1000

    form_overrides = dict(role=SelectField, membership_status=SelectField)
    form_args = dict(
        role = dict(choices=[(2, 'Member'), (1, 'Publisher'), (0, 'Administrator')], coerce=int),
        membership_status = dict(choices=[(0, 'Unregistered'), (1, 'In Progress (Unpaid)'), (2, 'Official (Paid)')], coerce=int)
    )

    def is_accessible(self):
        # Only accessible to those with an admin role.
        return g.user is not None and g.user.isAdmin()

    def __init__(self, session, **kwargs):
        # Just call parent class with predefined model.
        super(UserAdmin, self).__init__(User, session, name="user", endpoint="usertools", **kwargs)

class PostAdmin(ModelView):
    """
    A modification on ModelView that adds article administration.
    """
    excluded_list_columns = ['gfm_content']

    sortable_columns = (('category', Category.slug), ('author', User.name), 'title', 'created', 'slug')

    searchable_columns = (User.name,)

    list_formatters = dict(category=lambda m, p: m.category.slug,
                           author=lambda m, p: m.author.name,
                           created=lambda m, p: m.created.strftime("%b %d, %Y"),
                           slug=lambda m, p: m.slug.lower())

    form_overrides = dict(gfm_content=TextAreaField)
    excluded_form_columns = ('created')

    create_template = 'admin/posts/edit.html'
    edit_template = 'admin/posts/edit.html'

    def __init__(self, session, **kwargs):
        super(PostAdmin, self).__init__(Post, session, name="posts", endpoint="publish", url='/publish', **kwargs)   

    def is_accessible(self):
        # Only accessible to those with a publisher role.
        return g.user is not None and g.user.isPublisher()

class CategoryAdmin(ModelView):
    """
    A modification on ModelView that adds category administration.
    """
    searchable_columns = (Category.title, Category.slug)

    def __init__(self, session, **kwargs):
        super(CategoryAdmin, self).__init__(Category, session, name="category", endpoint="cats", url='/publish/cat', **kwargs)

    def is_accessible(self):
        # Only accessible to those with a publisher role.
        return g.user is not None and g.user.isPublisher()

class TagAdmin(ModelView):
    """
    A modification on ModelView that adds category administration.
    """
    searchable_columns = (Tag.name,)

    def __init__(self, session, **kwargs):
        super(TagAdmin, self).__init__(Tag, session, name="tags", endpoint="tags", url='/publish/tag', **kwargs)

    def is_accessible(self):
        # Only accessible to those with a publisher role.
        return g.user is not None and g.user.isPublisher()


class ReportAdmin(ModelView):
    """
    A modification on ModelView that adds report-creating options like generating paper copies
    of membership information.
    """
    excluded_list_columns = ['description', 'wepay_verification', 'signature', 'role', 'membership_status', 'wepay_checkout_id']
    searchable_columns = (User.name, User.email, User.netid, User.standing, User.major)

    # This view is for reports only so nothing is editable or creatable.
    can_create = False
    can_edit = False
    can_delete = False

    # Some impossible page size
    page_size = 1000

    list_formatters = dict(role=lambda m, p: USER.ROLE[m.role].title(),
                           membership_status=lambda m, p: USER.MEMBER_STATUS[m.membership_status].title(),
                           member_since=lambda m, p: m.member_since.strftime("%b %d, %Y"),
                           membership_paid_on=lambda m, p: m.membership_paid_on.strftime("%b %d, %Y") if m.membership_paid_on is not None else "Not Paid",
                           standing=lambda m, p: m.standing.title())

    def is_accessible(self):
        # Only accessible to those with an admin role.
        return g.user is not None and g.user.isAdmin()

    def __init__(self, session, **kwargs):
        super(ReportAdmin, self).__init__(User, session, name="report", endpoint="reports", **kwargs)

    @action('copy', lazy_gettext('Make Paper Copy'))
    def generate_paper_copy(self, users):
        """
        Turns user(s) information into zip package for download.
        """
        zipdata = StringIO.StringIO()
        zipped = zipfile.ZipFile(zipdata, "w")

        for user_id in users:
            user = User.query.get(user_id)

            # For each user, render the membership form template with user-specific data
            html = render_template("admin/report/membership_form_template.html", user=user)
            result = StringIO.StringIO()

            # Convert rendered xhtml into pdf file for specific user
            pdf = pisa.CreatePDF(StringIO.StringIO(html.encode("utf_8")), dest=result)

            if not pdf.err:
                # Add this user's unique pdf to the zip archive
                zipped.writestr(user.name + ".pdf", result.getvalue())
                result.close()
        zipped.close()
        # seek(0) to make sure response is read from the beginning of the StringIO buffer
        zipdata.seek(0)
        # Create a zip attachment using send_file
        response = send_file(zipdata, "application/zip", True, "membership_forms.zip")
        return response

