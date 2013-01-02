"""Decorators for the User views"""
from functools import wraps

from flask import g, redirect, url_for, request, current_app

def oauth_flow(f):
  """Passes app oauth flow object to calling function."""
  from oauth2client.client import OAuth2WebServerFlow
  @wraps(f)
  def decorated_function(*args, **kwargs):
    flow = OAuth2WebServerFlow(
      client_id=current_app.config['GOOGLE_CLIENT_ID'],
      client_secret=current_app.config['GOOGLE_CLIENT_SECRET'],
      scope='https://www.googleapis.com/auth/userinfo.email',
      redirect_uri=current_app.config['HOST_URL'] + '/oauth2callback')
    return f(flow, *args, **kwargs)
  return decorated_function
