from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for

# WePay transaction
from wepay import WePay
import hashlib, random, os, base64
from datetime import datetime

# Signature storage
from signpad2image.signpad2image import s2i
import StringIO

from acm_phoenix import db
from acm_phoenix.users import constants as USER
from acm_phoenix.users.forms import RegisterForm
from acm_phoenix.users.models import User
from acm_phoenix.users.decorators import requires_login

mod = Blueprint('users', __name__, url_prefix='')

@mod.route('/profile/')
def home():
  """
  Display User profile
  """
  return render_template("users/profile.html", user=g.user)

@mod.route('/login/', methods=['GET', 'POST'])
def login():
  """
  Login form
  """
  # form = LoginForm(request.form)
  # # make sure data are valid, but doesn't validate password is right
  # if form.validate_on_submit():
  #   user = User.query.filter_by(email=form.email.data).first()
  #   # we use werzeug to validate user's password
  #   if user and check_password_hash(user.password, form.password.data):
  #     # the session can't be modified as it's signed, 
  #     # it's a safe place to store the user id
  #     session['user_id'] = user.id
  #     flash('Welcome %s' % user.name)
  #     return redirect(url_for('users.home'))
  #   flash('Wrong email or password', 'error-message')
  # return render_template("users/login.html", form=form)
  
def wepay_membership_response(user):
  """
  Make a WePay API call for membership payment and return the response.
  """
  random_string = base64.urlsafe_b64encode(os.urandom(30))
  verification_key = hashlib.sha224(random_string + user.email +
                                    user.name).hexdigest()

  user.wepay_verification = verification_key
  db.session.commit()

  # Application settings
  account_id = 319493
  access_token = '6dd6802f8ebef4992308a0e4f7698c275781ac36854f9451127115d995d8cda7'
  production = False

  wepay = WePay(production, access_token)
  redirect_url = 'http://acm.frvl.us:5000/verify/' + verification_key

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
    # create an user instance not yet stored in the database
    raw_signature = request.form['output']
    
    # Convert drawn signature to base64 encoded image.
    if raw_signature.find("data:image") == -1:
      PIL_image = s2i(raw_signature,
                      input_image=os.path.abspath("acm_phoenix/static/packages/signpad2image/signpad2image/blanksig.png"),
                      nosig_image=os.path.abspath("acm_phoenix/static/packages/signpad2image/signpad2image/nosig.png"))
      output =  StringIO.StringIO()
      PIL_image.save(output, format="PNG")
      sig_img = "data:image/png;base64," + base64.b64encode(output.getvalue())
      output.close()
    else:
      sig_img = raw_signature

    user = User(form.name.data, form.netid.data, form.email.data, \
                  form.standing.data, form.major.data, form.sid.data, \
                  form.shirt_size.data, form.description.data, sig_img)
    user.member = True

    # Insert the record in our database and commit it
    db.session.add(user)
    db.session.commit()

    # Log the user in, as he now has an id
    session['user_id'] = user.id

    # flash will display a message to the user
    flash('Thanks for registering')

    
    if form.reg_and_pay.data == True:
      response = wepay_membership_response(user)
      return redirect(response['checkout_uri'])
    else:
      # redirect user to the 'home' method of the user module.
      return redirect(url_for('users.home'))
  return render_template("users/register.html", form=form)

@mod.route('/verify/<string:verification_key>')
def verify_membership_payment(verification_key):
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
    session['user_id'] = user.id

  return redirect(url_for('users.home'))
  
@mod.route('/paymembership/')
def payment_redirect():
  user = User.query.get(session['user_id'])
  response = wepay_membership_response(user)
  return redirect(response['checkout_uri'])
