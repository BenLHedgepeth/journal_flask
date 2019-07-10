import re
import datetime

from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField, TextAreaField,
                     DateField, IntegerField, SelectField, FieldList,
                     FormField, DateTimeField)
from wtforms.validators import DataRequired, Email, EqualTo, Regexp, Optional


class LoginForm(FlaskForm):
    user_name = StringField(
            label="Username",
            validators=[DataRequired(message="Username")])

    password = PasswordField(
            label="Password",
            validators=[DataRequired(message="Password")])

    submit = SubmitField(label="Login")


class RegisterForm(FlaskForm):

    user_name = StringField(
            label="Username",
            validators=[DataRequired(message="Username")])

    email = StringField(
            label="Email",
            validators=[
                DataRequired(message="Email"),
                Email(message="Invalid Email")])

    password = PasswordField(
            label="Password",
            validators=[DataRequired(message="Password"), EqualTo('confirm')])
    confirm = PasswordField(
            label="Confirm Password",
            validators=[DataRequired(message="Confirm Password")])

    submit = SubmitField(label="Register")


class TagForm(FlaskForm):
    tag1 = StringField(
            label="Tag 1",
            validators=[DataRequired()])

    tag2 = StringField(
            label="Tag 2",
            validators=[Optional()])


class JournalForm(FlaskForm):
    title = StringField(
            label="Title",
            validators=[DataRequired(message="Title")])

    date = DateTimeField(
        label='Date',
        default=datetime.datetime.now,
        format='%Y-%m-%d')

    time = IntegerField(
            label="Time spent (in minutes)",
            validators=[DataRequired(message="Time - Invalid time provided")])

    topic = TextAreaField(
            label="What did you learn...",
            validators=[DataRequired(message="Topic")])

    resources = TextAreaField(
            label="Add whatever resources you believe apply to the topic...",
            validators=[DataRequired(message="Resources")])

    tags = FieldList(FormField(TagForm), min_entries=1)

    submit = SubmitField(label="Submit Entry")


class EditJournalEntryForm(FlaskForm):
    title = StringField(validators=[DataRequired(message="Title")])

    time = IntegerField(validators=[DataRequired(message="Time")])

    topic = TextAreaField(validators=[DataRequired(message="Topic")])

    resources = TextAreaField(validators=[DataRequired(message="Resources")])


    submit = SubmitField(label="Submit Entry")
