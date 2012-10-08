"""Decorators for the User views"""
from functools import wraps

from flask import g, redirect, url_for, request

def requires_login(f):
  """
  Forces viewer to login when trying to access a certain function.
  """
  @wraps(f)
  def decorated_function(*args, **kwargs):
    if g.user is None:
      return redirect(url_for('users.login', next=request.path))
    return f(*args, **kwargs)
  return decorated_function
