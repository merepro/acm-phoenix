from acm_phoenix.users.models import User
from flask import flash
from flask.ext.admin.contrib.sqlamodel import ModelView
from flask.ext.admin import expose
from flask.ext.admin.actions import action
from flask.ext.admin.babel import gettext, lazy_gettext

class UserAdmin(ModelView):
    """
    A modification on ModelView that removes extraneous columns like Description,
    WePay Verification Key, and Signature
    """
    excluded_list_columns = ['description', 'wepay_verification', 'signature']

    # Only text based columns are searchable anyways.
    searchable_columns = (User.name, User.email, User.netid, User.standing, User.major)

    def __init__(self, session, **kwargs):
        # Just call parent class with predefined model.
        super(UserAdmin, self).__init__(User, session, name="user", endpoint="usertools", **kwargs)

class ReportAdmin(ModelView):
    """
    A modification on ModelView that adds report-creating options like generating paper copies
    of membership information.
    """
    excluded_list_columns = ['description', 'wepay_verification', 'signature', 'role', 'membership_status']
    searchable_columns = (User.name, User.email, User.netid, User.standing, User.major)

    # This view is for reports only so nothing is editable or creatable.
    can_create = False
    can_edit = False
    can_delete = False

    def __init__(self, session, **kwargs):
        super(ReportAdmin, self).__init__(User, session, name="report", endpoint="reports", **kwargs)

    @action('copy', lazy_gettext('Make Paper Copy'))
    def generate_paper_copy(self, users):
        """
        Turns user(s) information into pdf/package for download.
        """
        flash(gettext('Generating Copies'))
