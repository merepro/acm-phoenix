from flask.ext.wtf import Form, TextField, IntegerField, SelectField, TextAreaField, SubmitField
from flask.ext.wtf import Required, Email, EqualTo

class RegisterForm(Form):
    name = TextField(u'Full Name', [Required()])
    netid = TextField(u'NetID', [Required()])
    email = TextField(u'Email address', [Required(), Email()])
    standing = SelectField(u'Class Standing', [Required()], choices=[('freshman', 'Freshman'), ('soph', 'Sophomore'), ('junior', 'Junior'), ('senior', 'Senior'), ('alum', 'Alumni'), ('grad', 'Graduate Student'), ('faculty', 'Faculty')])
    major = SelectField(u'Major', [Required()], choices=[('CS', 'CS (Computer Science)'), ('CE', 'CE (Computer Engineering)'), ('BI', 'BI (Business Informatics)'), ('Other', 'Other')])
    shirt_size = SelectField(u'T-Shirt Size', [Required()], choices=[('S', 'Small'), ('M', 'Medium'), ('L', 'Large'), ('XL', 'X-Large'), ('XXL', '2X-Large')])
    description = TextAreaField(u'Describe yourself! (Github Flavored Markdown Allowed!)')
    reg_only = SubmitField(u'<i class="icon-group"></i> Register Only')
    reg_and_pay = SubmitField(u'<i class="icon-credit-card"></i> Register and Pay Membership')

class EditForm(Form):
    name = TextField(u'Name', [Required()])
    netid = TextField(u'NetID', [Required()])
    email = TextField(u'Email address', [Required()])
    standing = SelectField(u'Class Standing', [Required()], choices=[('freshman', 'Freshman'), ('soph', 'Sophomore'), ('junior', 'Junior'), ('senior', 'Senior'), ('alum', 'Alumni'), ('grad', 'Graduate Student'), ('faculty', 'Faculty')])
    major = SelectField(u'Major', [Required()], choices=[('CS', 'CS (Computer Science)'), ('CE', 'CE (Computer Engineering)'), ('BI', 'BI (Business Informatics)'), ('Other', 'Other')])
    shirt_size = SelectField(u'T-Shirt Size', [Required()], choices=[('S', 'Small'), ('M', 'Medium'), ('L', 'Large'), ('XL', 'X-Large'), ('XXL', '2X-Large')])
    description = TextAreaField(u'Describe yourself! (Github Flavored Markdown Allowed!)')
    
