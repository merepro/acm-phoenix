from flask import Blueprint, request, render_template, g, session, redirect, url_for

from acm_phoenix import db
from acm_phoenix.users.models import User
from acm_phoenix.users.decorators import requires_login

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/')
def admin_home():
    """
    Show the homepage for the administration panel
    """
    return render_template("admin/main_panel.html", user=g.user)
