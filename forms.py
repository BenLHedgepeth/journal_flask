import re
import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateField, IntegerField, SelectField, FieldList, FormField
from wtforms.validators import DataRequired, Email, EqualTo, Regexp, Optional


class LoginForm(FlaskForm):
    user_name = StringField(
            label="Username",
            validators=[DataRequired()]
        )
    password = PasswordField(
            label="password",
            validators=[DataRequired()]
        )
    submit = SubmitField(
            label="Login"
        )


class RegisterForm(FlaskForm):

    user_name = StringField(
            label="Username",
            validators=[DataRequired()]
        )
    email = StringField(
            label="Email",
            validators=[DataRequired(), Email(message="Invalid Email")]
        )
    password = PasswordField(
            label="Password",
            validators=[DataRequired(), EqualTo('confirm')]
        )
    confirm = PasswordField(
            label="Confirm Password",
            validators=[DataRequired()]
        )
    submit = SubmitField(
            label="Register"
        )

class TagForm(FlaskForm):
    tag1 = StringField(
            label="Tag 1",
            validators=[DataRequired()]
        )
    tag2 = StringField(
            label="Tag 2",
            validators=[Optional()]
        )


class JournalForm(FlaskForm):
    title = StringField(
            label="Title",
            validators=[DataRequired()]
        )

    time = IntegerField(
            label="Time spent (in minutes)",
            validators=[DataRequired()]
        )

    topic = TextAreaField(
            label="What did you learn...",
            validators=[DataRequired()]
        )
    resources = TextAreaField(
            label="Add whatever resources you believe apply to the topic..."
        )
    tags = FieldList(FormField(TagForm), min_entries=1)
 
    submit = SubmitField(
            label="Submit Entry"
        )


class EditJournalEntryForm(FlaskForm):
    title = StringField(validators=[Optional()])

    time = IntegerField(validators=[Optional()])

    topic = TextAreaField(validators=[Optional()])

    resources = TextAreaField(validators=[Optional()])   

    tags = FieldList(
        FormField(TagForm),
        validators=[Optional()], 
        min_entries=1)
 
    submit = SubmitField(
            label="Submit Entry"
        )




