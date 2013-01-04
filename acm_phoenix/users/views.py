"""Views for the users module"""
from flask import (Blueprint, request, render_template, flash, session,
                   redirect, url_for, current_app, abort)
from flask.ext.login import login_required, login_user, current_user

# WePay transaction
from wepay import WePay
import hashlib, os, base64
from datetime import datetime

# Signature storage
import signpad2image
import StringIO

from acm_phoenix.extensions import db
from acm_phoenix.views import mod as indexModule
from acm_phoenix.users import constants as USER
from acm_phoenix.users.forms import RegisterForm, EditForm
from acm_phoenix.users.models import User
from acm_phoenix.users.decorators import oauth_flow
from oauth2client.client import FlowExchangeError

# Github Flavored Markdown
from acm_phoenix.users.gfm import gfm

# User Blueprint
mod = Blueprint('users', __name__, url_prefix='')

# Routing rules
@mod.route('/profile/')
@login_required
def home():
  """
  Display User profile
  """
  return render_template('users/profile.html', user=current_user)

@mod.route('/profile/edit/', methods=['GET', 'POST'])
@login_required
def edit_profile():
  """
  Allow User to edit their profile info
  """
  form = EditForm(request.form)
  if form.validate_on_submit():
    # Checking if someone is trying to change their email to another user's.
    otherUser = User.query.filter_by(netid=form.netid.data,
                                     email=form.email.data).first()

    # The user with the new netid and email either shouldn't exist or
    # should be the current user.
    if otherUser is not None and current_user != otherUser:
      flash(u'You seem to be trying to change your netid/email'
            ' to someone else\'s', 'error')
      return redirect(url_for('users.home'))

    current_user.name = form.name.data
    current_user.netid = form.netid.data
    current_user.email = form.email.data
    current_user.standing = form.standing.data
    current_user.major = form.major.data
    current_user.shirt_size = form.shirt_size.data
    current_user.description = gfm(form.description.data)
    
    db.session.add(current_user)
    db.session.commit()
    return redirect(url_for('users.home'))
  return render_template('users/edit.html', user=current_user, form=form)

@mod.route('/login/')
@oauth_flow
def login(flow):
  """
  Login with rmail account using Google OAuth2
  """
  session['next_path'] = request.args.get('next')
  if session['next_path'] is None:
    session['next_path'] = url_for('users.home')

  if current_user.is_authenticated():
    return redirect(session['next_path'])
  else:
    auth_uri = flow.step1_get_authorize_url()
    return redirect(auth_uri)

def wepay_membership_response(user):
  """
  Make a WePay API call for membership payment and return the response.
  """
  # Generate verification_key for wepay payment.
  random_string = base64.urlsafe_b64encode(os.urandom(30))
  verification_key = hashlib.sha224(random_string + user.email +
                                    user.name).hexdigest()

  user.wepay_verification = verification_key
  db.session.commit()

  # WePay Application settings
  account_id = current_app.config['WEPAY_ACCT_ID']
  access_token = current_app.config['WEPAY_ACC_TOK']
  production = current_app.config['WEPAY_IN_PROD']

  wepay = WePay(production, access_token)
  redirect_url = current_app.config['HOST_URL'] + \
      url_for('users.verify_membership_payment',
              verification_key=verification_key)

  response = wepay.call('/checkout/create', {
      'account_id': account_id,
      'amount': '20.00',
      'short_description': '1 year ACM Club Membership',
      'mode': 'regular',
      'type': 'SERVICE',
      'redirect_uri': redirect_url
  })

  return response

@mod.route('/register/', methods=['GET', 'POST'])
def register():
  """
  Registration Form
  """
  form = RegisterForm(request.form)
  if form.validate_on_submit():
    # If netid and email are unique, create an user instance not yet
    # stored in the database
    user = User.query.filter_by(netid=form.netid.data,
                                email=form.email.data).first()
    if user:
      flash(u'NetID/Email already registered', 'error')
      return render_template("users/register.html", form=form)

    raw_signature = request.form['output']
    
    # Convert drawn signature to base64 encoded image.
    if raw_signature.find("data:image") == -1:
      from signpad2image import s2i

      PIL_image = s2i(
        raw_signature,
        input_image=os.path.abspath('acm_phoenix/static/packages/signpad2image'
                                    '/signpad2image/blanksig.png'),
        nosig_image=os.path.abspath('acm_phoenix/static/packages/signpad2image'
                                    '/signpad2image/nosig.png'))

      output =  StringIO.StringIO()
      PIL_image.save(output, format='PNG')
      sig_img = 'data:image/png;base64,' + base64.b64encode(output.getvalue())
      output.close()
    else:
      sig_img = raw_signature

    user = User(form.name.data, form.netid.data, form.email.data,
                form.standing.data, form.major.data,
                form.shirt_size.data, gfm(form.description.data), sig_img)
    user.member = True

    # Insert the record in our database and commit it
    db.session.add(user)
    db.session.commit()

    login_user(user)

    # flash will display a message to the user
    flash('Thanks for registering')
    
    # If user wants to pay membership now, redirect them to wepay.
    if form.reg_and_pay.data:
      response = wepay_membership_response(user)
      
      # Keep track of user's checkout_id for later lookup on wepay.
      user.wepay_checkout_id = response['checkout_id']
      db.session.add(user)
      db.session.commit()
      return redirect(response['checkout_uri'])
    else:
      # redirect user to the 'home' method of the user module.
      return redirect(url_for('users.home'))
  return render_template('users/register.html', form=form)

@mod.route('/verify/<string:verification_key>')
@login_required
def verify_membership_payment(verification_key):
  """
  Verifies that a user paid their membership by checking redirected key
  to a User record.
  """
  # Notice that accepting verification_key as a string automatically cuts off
  # the trailing ?checkout_uri=##### from the WePay redirect.
  user = User.query.filter_by(wepay_verification=verification_key).first()
  if user:
    flash('Your membership payment has been received. Thank you!;')
    user.membership_status = USER.PAID
    user.member_since = datetime.now()
    user.membership_paid_on = user.member_since
    db.session.add(user)
    db.session.commit()

  return redirect(url_for('users.home'))
  
@mod.route('/paymembership/')
@login_required
def payment_redirect():
  """
  Redirects user to wepay page.
  """
  user = current_user
  response = wepay_membership_response(user)
  user.wepay_checkout_id = response['checkout_id']
  db.session.add(user)
  db.session.commit()
  return redirect(response['checkout_uri'])

@mod.route('/oauth2callback/')
@oauth_flow
def authenticate_user(flow):
  """
  Authenticate user as logged in after Google OAuth2 sends a callback.
  """
  # Get OAuth2 authentication code
  code = request.args.get('code')
  error = request.args.get('error')
  if error or code is None:
    flash(u'There was an error authenticating you. Please again.', 'error')
    return redirect(url_for('index.show_home'))

  try:
    # Exchange code for fresh credentials
    credentials = flow.step2_exchange(code)
    return verify_credentials_and_login(credentials)
  except FlowExchangeError:
    abort(403)

def verify_credentials_and_login(credentials):
  id_token = credentials.id_token
  if id_token is None:
    flash(u'Invalid login credentials', 'error')
    return redirect(url_for('index.show_home'))

  # Extract email and email verification
  email = id_token['email']
  verified_email = id_token['verified_email']

  if verified_email == 'true':
    # Find user with this email
    user = User.query.filter_by(email=email).first()
    if user is None:
      flash(u'We couldn\'t find any users with that email. '
            'You must register to be a member before logging '
            'in with rmail', 'error')
      return redirect(url_for('users.register'))
    else:
      # Log them in and send them to their request destination.
      login_user(user, remember=False)
      if 'next_path' not in session:
        session['next_path'] = url_for('users.home')

      return redirect(session['next_path'])
  else:
    flash(u'Sorry, we couldn\'t verify your email', 'error')
    return redirect(url_for('index.show_home'))

@mod.route('/user/view/<user_netid>/')
@login_required
def view_profile(user_netid):
  """
  Displays a user page by clicking on their mini-gravatar icon
  in the About Us page
  """
  user = User.query.filter_by(netid=user_netid).first()
  #If the user clicked is the user himself, display his profile home
  if user == current_user and current_user.is_authenticated():
    return render_template('users/profile.html', user=current_user)
  #Otherwise, display the profile page for other users
  elif user is not None:
    return render_template('users/view.html', user=user)
  else:
    flash(u'Sorry, we couldn\'t find the user you asked for.', 'error')
    return redirect(url_for('users.home'))
