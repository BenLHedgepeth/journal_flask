

import models
import views

from instance.config import BaseConfig

from flask import Flask, render_template, g, flash, url_for, redirect
from flask.views import View
from flask_login import LoginManager, login_user, login_required, current_user
from flask_bcrypt import Bcrypt

import forms

from helpers import verify_login_credentials

app = Flask(__name__, instance_relative_config=True)
app.config.from_object(BaseConfig.setup_app_config())
models.database.init(app.config['DATABASE'])
models.initialize_tables()

login_manager = LoginManager(app)
login_manager.init_app(app)

bcrypt = Bcrypt(app)

@app.before_request
def before_request():
  g.db = models.database
  g.user = current_user

  g.db.connect(reuse_if_open=True)




class LoginView(View):

  def __init__(self, form, template):
    self.form = form
    self.template = template

  def dispatch_request(self):
    login = self.form()

    if login.validate_on_submit():
      user = verify_login_credentials(login)
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


class RegisterView(LoginView):
  def __init__(self, form, template):
    super().__init__(form, template)

  def dispatch_request(self):
    register = self.form()
    if register.validate_on_submit():
        import pdb; pdb.set_trace()
        try:
            models.Writer.create_writer(
                user_name = register.user_name.data,
                email = register.email.data,
                password = bcrypt.generate_password_hash(
                                  register.password.data)
            )
        except ValueError:
            flash(f"Registration failed. An active account exists. Please log in.")
            return redirect(url_for('register'))
        else:
            flash("Your account has been created!")
            return redirect(url_for("home"))
    return render_template(self.template, form=register)




class HomeView(View):

  template = 'layout.html'

  def dispatch_request(self):
    return render_template(self.template)

class NewJournalEntryView(View):

    def __init__(self, form, template):
        self.form = form
        self.template = template

    @login_required
    def dispatch_request(self):
        entry = self.form()
        return render_template(self.template, form=entry)


app.add_url_rule('/', view_func=HomeView.as_view('home'), methods=['GET'])
app.add_url_rule('/login', view_func=LoginView.as_view('login', form=forms.LoginForm, template='login.html'), methods=['GET', 'POST'])
app.add_url_rule('/register', view_func=RegisterView.as_view('register', form=forms.RegisterForm, template='register.html'), methods=['GET', 'POST'])
# app.add_url_rule('/entries/new', view_func=NewJournalEntryView.as_view('new_entry', form=forms.JournalForm, template='new.html'), methods=['GET', 'POST'])

