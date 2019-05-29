import re
import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Regexp


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


class JournalForm(FlaskForm):
    title = StringField(
            label="Title",
            validators=[DataRequired()]
        )

    time = IntegerField(
            label="Time spent (in minutes)",
            validators=[DataRequired()]
        )

    topic_learned = TextAreaField(
            label="What did you learn...",
            validators=[DataRequired()]
        )
    resources = TextAreaField(
            label="Add whatever resources you believe apply to the topic..."
        )

    submit = SubmitField(
            label="Submit Entry"
        )
