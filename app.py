

import models
import views

from instance.config import BaseConfig

from flask import Flask, render_template
from flask.views import View
from flask_login import LoginManager, login_user
from flask_bcrypt import Bcrypt

import forms

app = Flask(__name__, instance_relative_config=True)
app.config.from_object(BaseConfig.setup_config())
models.database.init(app.config['DATABASE'])
models.initialize_tables()

login_manager = LoginManager(app)
login_manager.init_app(app)

bcrypt = Bcrypt(app)



class LoginView(View):

  def __init__(self, form, template):
    self.form = form
    self.template = template

  def dispatch_request(self):
    login = self.form()

    if login.validate_on_submit():
      user = self.verify_login(login)
      if user:
        login_user(user)
        flash("Login Successful", 'success')
        return redirect(url_for('index'))
      elif not login_user:
        flash("That account does not exist. Sign up to join!", 'info')
      else:
        flash("Invalid username and/or password", 'info')
      return redirect(url_for('login'))
    return render_template('login.html', form=login)

  def verify_login(self, form):
    site_member = models.Writer.get_or_none(
      models.Writer.user_name == form.user_name.data
    )
    if site_member:
      stored_password = site_member.password
      provided_password = form.password.data
      password_accepted = flask_bcrypt.check_password_hash(
        stored_password, provided_password
      )

      if password_accepted:
        return site_member
      elif not password_accepted:
        return None
    return  

class RegisterView(LoginView):
  def __init__(self, form, template):
    super().__init__(form, template)

  def dispatch_request(self):
    register = self.form()

    if register.validate_on_submit():
      approved = self.check_registeration(register)
      if approved:
        models.Writer.create_writer(
            last_name = register.last_name.data,
              first_name = register.first_name.data,
              user_name = register.user_name.data,
              email = register.email.data,
              password = bcrypt.generate_password_hash(
                    register.password.data
                  )
          )
        flash("Your account has been created!")
        return redirect(url_for("index"))
      flash("Registration failed. The {site_account[1]} provided has an active account. Please log in.")
      return redirect(url_for('register'))
    return render_template(self.template, form=register)

  def check_registeration(self, form):
    email_taken = (models.Writer.get_or_none(
      models.Writer.email == form.email.data), 'email')
    username_taken = (models.Writer.get_or_none(
      models.Writer.username == form.username.data), 'username')

    site_account = any(data[0] == True for data in [email_taken, username_taken])

    return site_account


class HomeView(View):

  template = 'layout.html'

  def dispatch_request(self):
    return render_template(self.template)

class NewJournalEntryView(View):

    def __init__(self, form, template):
        self.form = form
        self.template = template

    def dispatch_request(self):
        entry = self.form()
        return render_template(self.template, form=entry)


app.add_url_rule('/', view_func=HomeView.as_view('index'), methods=['GET'])
app.add_url_rule('/login', view_func=LoginView.as_view('login', form=forms.LoginForm, template='login.html'), methods=['GET', 'POST'])
app.add_url_rule('/register', view_func=RegisterView.as_view('register', form=forms.RegisterForm, template='register.html'), methods=['GET', 'POST'])
app.add_url_rule('/entries/new', view_func=NewJournalEntryView.as_view('new_entry', form=forms.JournalForm, template='new.html'), methods=['GET', 'POST'])

