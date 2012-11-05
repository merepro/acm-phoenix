"""Views for site content snippets"""
from flask import (Blueprint, request, render_template, flash, g, session,
                   redirect, url_for)

from acm_phoenix.users.models import User

mod = Blueprint('snippets', __name__, url_prefix='')

# Routing rules
@mod.route('/mission/')
def show_mission_snippet():
    """
    Displays ACM's Mission statement.
    """
    return render_template('snippets/mission.html')

@mod.route('/about/')
def show_about_us():
    """
    Displays information about the organization.
    """
    users = User.query.all()
    return render_template('snippets/about.html', users=users)
