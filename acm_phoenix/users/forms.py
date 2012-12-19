"""Defines the Registration and Profile Edit forms for users."""

from flask.ext.wtf import (Form, TextField, IntegerField, SelectField, 
                           TextAreaField, SubmitField)
from flask.ext.wtf import Required, Email, EqualTo, Optional

class RegisterForm(Form):
    """
    Registration Form to fill out initial User object.
    """
    name = TextField(u'Full Name', [Required()])
    netid = TextField(u'NetID', [Required()])
    email = TextField(u'Email address', [Required(), Email()])
    standing = SelectField(
        u'Class Standing', [Required()],
        choices=[('freshman', 'Freshman'),
                 ('soph', 'Sophomore'),
                 ('junior', 'Junior'),
                 ('senior', 'Senior'),
                 ('alum', 'Alumni'),
                 ('grad', 'Graduate Student'),
                 ('faculty', 'Faculty')]
        )

    major = SelectField(
        u'Major', [Required()],
        choices=[('CS', 'CS (Computer Science)'),
                 ('CE', 'CE (Computer Engineering)'),
                 ('BI', 'BI (Business Informatics)'),
                 ('Other', 'Other')]
        )

    shirt_size = SelectField(
        u'T-Shirt Size', [Required()],
        choices=[('S', 'Small'),
                 ('M', 'Medium'),
                 ('L', 'Large'),
                 ('XL', 'X-Large'),
                 ('XXL', '2X-Large')]
        )

    description = TextAreaField(u'Describe yourself! '
                                '(Github Flavored Markdown Allowed!)',
                                [Optional()])

    reg_only = SubmitField(u'<i class="icon-group"></i> Register Only')
    reg_and_pay = SubmitField(u'<i class="icon-credit-card"></i> '
                              'Register and Pay Membership')

class EditForm(Form):
    """
    Form used to edit user profile information.
    """
    name = TextField(u'Name', [Required()])
    netid = TextField(u'NetID', [Required()])
    email = TextField(u'Email address', [Required(), Email()])

    standing = SelectField(
        u'Class Standing', [Required()],
        choices=[('freshman', 'Freshman'),
                 ('soph', 'Sophomore'),
                 ('junior', 'Junior'),
                 ('senior', 'Senior'),
                 ('alum', 'Alumni'),
                 ('grad', 'Graduate Student'),
                 ('faculty', 'Faculty')]
        )

    major = SelectField(
        u'Major', [Required()],
        choices=[('CS', 'CS (Computer Science)'),
                 ('CE', 'CE (Computer Engineering)'),
                 ('BI', 'BI (Business Informatics)'),
                 ('Other', 'Other')]
        )

    shirt_size = SelectField(
        u'T-Shirt Size', [Required()],
        choices=[('S', 'Small'),
                 ('M', 'Medium'),
                 ('L', 'Large'),
                 ('XL', 'X-Large'),
                 ('XXL', '2X-Large')]        
        )

    description = TextAreaField(u'Describe yourself! '
                                '(Github Flavored Markdown Allowed!)',
                                [Optional()])
    
