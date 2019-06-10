
import logging

import models
import views

from instance.config import BaseConfig

from flask import Flask, render_template, g, flash, url_for, redirect, current_app
from flask.views import View
from flask_login import LoginManager, login_user, login_required, current_user
from flask_bcrypt import Bcrypt

import forms


app = Flask(__name__, instance_relative_config=True)
app.config.from_object(BaseConfig.setup_app_config())
models.database.init(app.config['DATABASE'])
models.initialize_tables()

login_manager = LoginManager(app)
login_manager.init_app(app)

@login_manager.user_loader
def user_loader(id):
    return models.Writer.get_or_none(models.Writer.id == id)

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
            import pdb; pdb.set_trace()
            user = self.verify_login_credentials(login)
            if user:
                login_user(user)
                flash("Login Successful!", 'success')
                return redirect(url_for('home'))
            elif not login_user:
                flash("That account does not exist. Sign up to join!", 'info')
            else:
                flash("Invalid username and/or password", 'error')
            return redirect(url_for('login'))
        return render_template('login.html', form=login)


    def verify_login_credentials(self, form):
        site_member = models.Writer.get_or_none(
          models.Writer.user_name == form.user_name.data
        )
        if site_member:
          stored_password = site_member.password
          provided_password = form.password.data
          app.logger.debug(f'User hashed password retrieved: {stored_password}')
          password_accepted = bcrypt.check_password_hash(stored_password, provided_password)

          if password_accepted:
            return site_member
          elif not password_accepted:
            return None
        return  




class RegisterView(LoginView):
    def __init__(self, form, template):
        super().__init__(form, template)

    def dispatch_request(self):
        form = self.form()
        if form.validate_on_submit():
            try:
                models.Writer.create_writer(
                    user_name = form.user_name.data,
                    email = form.email.data,
                    password = bcrypt.generate_password_hash(
                                      form.password.data)
                )
            except ValueError:
                flash(f"Registration failed. An active account exists. Please log in.")
                return redirect(url_for('register'))
            else:
                flash("Your account has been created!")
                return redirect(url_for("home"))
        return render_template(self.template, form=form)




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

