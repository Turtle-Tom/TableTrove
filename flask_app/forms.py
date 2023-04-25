from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import (
    InputRequired,
    DataRequired,
    NumberRange,
    Length,
    Email,
    EqualTo,
    ValidationError,
)


from .models import User

import re


class SearchForm(FlaskForm):
    search_query = StringField(
        "Query", validators=[InputRequired(), Length(min=1, max=100)]
    )
    submit = SubmitField("Search")


class ItemCommentForm(FlaskForm):
    text = TextAreaField(
        "Comment", validators=[InputRequired(), Length(min=5, max=500)]
    )
    submit = SubmitField("Enter Comment")

class ItemLikeForm(FlaskForm):
    submit_like = SubmitField("♥")

class CreateItemForm(FlaskForm):
    name = StringField(
        "Item name",
        validators=[InputRequired(), Length(min=1, max=50)]
    )
    content = TextAreaField(
        "Description",
        validators=[InputRequired(), Length(min=5, max=500)]
    )
    submit = SubmitField("Create Item")


class CreatureCommentForm(FlaskForm):
    text = TextAreaField(
        "Comment", validators=[InputRequired(), Length(min=5, max=500)]
    )
    submit = SubmitField("Enter Comment")


class CreatureLikeForm(FlaskForm):
    submit_like = SubmitField("♥")


class CreateCreatureForm(FlaskForm):
    name = StringField(
        "Creature name",
        validators=[InputRequired(), Length(min=1, max=50)]
    )
    content = TextAreaField(
        "Description",
        validators=[InputRequired(), Length(min=5, max=500)]
    )
    submit = SubmitField("Create Creature")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", 
    validators=[
        InputRequired(),
        Length(min=8, max=40)
    ])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_pass(self, password):

        # Check for at least one number
        if not any(char.isdigit() for char in password):
            raise ValidationError("Password must contain a number")

        # Check for at leastt one special character
        if not bool(re.search(r'[!@#$%\^&*_\-?]', password)):
            raise ValidationError("Password must contain one of the following characters: !@#$%^&*_-?")

        # Check for at least one capital letter
        if not bool(re.search(r'[A-Z]', password)):
            raise ValidationError("Password must contain an uppercase letter")

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user is not None:
            raise ValidationError("Username is taken")

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user is not None:
            raise ValidationError("Email is taken")


class LoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    password = PasswordField("Password", 
    validators=[
        InputRequired(),
        Length(min=8, max=40)
    ])

    submit = SubmitField("Login")


class UpdateUsernameForm(FlaskForm):
    name = StringField(
        "Change Username", validators=[InputRequired(), Length(min=1, max=40)]
    )

    submit_name = SubmitField("Change Name")

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user is not None:
            raise ValidationError("Username is taken")


class UpdateProfilePicForm(FlaskForm):
    picture = FileField('Change Photo', validators=[
        FileAllowed(['jpg', 'png'], 'Images Only!')
    ])

    submit_pic = SubmitField('Update')


class DeleteAccountForm(FlaskForm):
    text = StringField(
        "Type \"DELETE\" prior to submission to confirm account deletion", validators=[InputRequired(), Length(min=1, max=40)]
    )

    submit_delete = SubmitField("Delete Account")

    def validate_confirmation(self, text):
        if text != "DELETE":
            raise ValidationError("Please type DELETE")
