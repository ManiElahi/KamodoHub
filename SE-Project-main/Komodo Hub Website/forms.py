# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SelectField, SubmitField, DecimalField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from flask_wtf.file import FileAllowed, FileField

# --- User Registration Form ---
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('teacher', 'Teacher'), ('student', 'Student'), ('community', 'Community Member')], validators=[DataRequired()])
    submit = SubmitField('Register')

# --- User Login Form ---
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# --- Wildlife Sighting Report Form ---
class ReportSightingForm(FlaskForm):
    species = StringField('Species', validators=[DataRequired(), Length(min=2, max=100)])
    location = StringField('Location', validators=[DataRequired(), Length(min=2, max=100)])
    media = FileField('Upload Image (optional)', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])
    notes = TextAreaField('Notes (optional)', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit Sighting')

# --- Content Submission Form (Digital Library) ---
class ContentSubmissionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    media = FileField('Attach Image/Media (optional)', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'mp4'], 'Images and videos only!')])
    is_public = SelectField('Visibility', choices=[('1', 'Public'), ('0', 'Private')], validators=[DataRequired()])
    submit = SubmitField('Submit Content')

# --- Message Form ---
class MessageForm(FlaskForm):
    receiver = SelectField('To', coerce=str, validators=[DataRequired()])
    content = TextAreaField('Message', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Send')

# --- Donation / Payment Form ---
class PaymentForm(FlaskForm):
    amount = DecimalField('Amount', places=2, rounding=None, validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Donate')
