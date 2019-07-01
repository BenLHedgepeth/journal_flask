
from flask import (Flask, render_template, g, flash,
                   url_for, redirect, current_app, request)

from flask.views import View

from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)

from flask_bcrypt import Bcrypt

from slugify import slugify

import models

import forms

from instance.config import BaseConfig

app = Flask(__name__, instance_relative_config=True)
app.config.from_object(BaseConfig.setup_app_config())
models.database.init(app.config['DATABASE'])
models.initialize_tables()

login_manager = LoginManager(app)
login_manager.init_app(app)


@login_manager.user_loader
def user_loader(id):
    return models.Writer.get_or_none(models.Writer.id == id)


@login_manager.unauthorized_handler
def unauthorized():
    return render_template('login.html')

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
            user = models.Writer.get_or_none(
                models.Writer.user_name == login.user_name.data
             )
            if not user:
                flash("That account does not exist. Sign up to join!", 'info')
                return redirect(url_for('login'))
            verified = bcrypt.check_password_hash(
                        user.password, login.password.data
                       )
            if not verified:
                flash("Invalid username and/or password", 'error')
                return redirect(url_for('login'))
            login_user(user)
            flash("Login Successful!", 'success')
            return redirect(url_for('home'))
        return render_template('login.html', form=login)

app.add_url_rule(
     '/login',
     view_func=LoginView.as_view(
         'login',
         form=forms.LoginForm,
         template='login.html'),
     methods=['GET', 'POST'])


class RegisterView(LoginView):
    def __init__(self, form, template):
        super().__init__(form, template)

    def dispatch_request(self):

        form = self.form()
        if form.validate_on_submit():
            try:
                models.Writer.create_writer(
                    user_name=form.user_name.data,
                    email=form.email.data,
                    password=form.password.data
                )
            except ValueError:
                flash(f"An active account exists. Please log in.")
                return redirect(url_for('register'))
            else:
                flash("Your account has been created!")
                return redirect(url_for("home"))
        return render_template(self.template, form=form)

app.add_url_rule(
    '/register',
    view_func=RegisterView.as_view(
         'register',
         form=forms.RegisterForm,
         template='register.html'),
    methods=['GET', 'POST'])


class IndexView(View):

    def __init__(self, template):
        self.template = template

    def dispatch_request(self, tag=None):

        if not tag:
            journal_entries = models.JournalEntry.select()
        else:
            journal_entries = (
                models.JournalEntry.select()
                .join(models.JournalEntryTag)
                .join(models.Tag)
                .where(models.Tag.name == tag))
        return render_template(self.template, journal_entries=journal_entries)

app.add_url_rule(
    '/',
    view_func=IndexView.as_view(
        'home',
        template='layout.html'
        ),
    methods=['GET'])

app.add_url_rule(
     '/entries',
     view_func=IndexView.as_view(
        'entries',
        template='layout.html'),
     methods=['GET'])

app.add_url_rule(
    '/entries/<tag>',
    view_func=IndexView.as_view(
        'tagged',
        template='layout.html'
        ),
    methods=['GET']
    )


class NewJournalEntryView(View):

    def __init__(self, form, template):
        self.form = form
        self.template = template

    @login_required
    def dispatch_request(self):
        entry = self.form()
        if entry.validate_on_submit():
            setattr(entry, 'writer', current_user._get_current_object())
            try:
                current_user.write_entry(entry)
            except ValueError:
                flash(f"'{entry.title.data}' exists...please edit as needed.")
                redirect(url_for('add_entry'))
            else:
                new_entry = models.JournalEntry.get(
                    models.JournalEntry.title == entry.title.data
                 )

                """Using a FieldList for the JournalForm 'tags' class
                attribute creates a built-in list. This list contains a
                dictionary of key-value pairs resembling the class that is
                passed as an argument to the FieldList when the form is
                submitted."""

                """https://wtforms.readthedocs.io/en/stable/
                   fields.html#wtforms.fields.FieldList"""

                """entry.tags.data[0] refers to this
                   dictionary as described above"""
                for tag_name, value in entry.tags.data[0].items():
                    tag_value = value.lower()
                    if tag_name != " " and tag_name != "csrf_token":
                        tag, created = models.Tag.get_or_create(
                            name=tag_value
                        )

                        models.JournalEntryTag.create(
                            journal_entry=new_entry,
                            journal_tag=tag
                         )
                flash("Your journal entry has been saved!")
                return redirect(url_for("home"))
        return render_template(self.template, form=entry)

app.add_url_rule(
    '/entries/new',
    view_func=(NewJournalEntryView.as_view(
        'add_entry',
        form=forms.JournalForm,
        template='new.html')),
    methods=['GET', 'POST'])


class JournalEntryDetailView(View):

    def __init__(self, template):
        self.template = template

    @login_required
    def dispatch_request(self, tag, slug):
        journal_data = current_user.retrieve_entry(slug)
        if not journal_data:
            return "Hello"
        else:

            tags = journal_data[1]
            return render_template(
                'detail.html',
                entry=journal_data[0],
                tags=journal_data[1]
            )


app.add_url_rule(
    '/entries/<tag>/<slug>',
    view_func=(JournalEntryDetailView.as_view(
         'entry',
         template='detail.html')),
    methods=['GET'])


class EditJournalView(View):

    def __init__(self, template, form):
        self.template = template
        self.form = form

    @login_required
    def dispatch_request(self, slug):
        writer_entry = current_user.retrieve_entry(slug)
        edit_journal_entry = self.form()

        if edit_journal_entry.validate_on_submit():
            writer_entry[0].title = request.form['title']
            writer_entry[0].time = request.form['time']
            writer_entry[0].topic = request.form['topic']
            writer_entry[0].resources = request.form['resources']
            writer_entry[0].save()
            flash("Journal entry updated!")
            return redirect(url_for('home'))

        return render_template(
            self.template,
            form=edit_journal_entry,
            entry=writer_entry[0],
            tags=writer_entry[1],
            )

app.add_url_rule(
    '/entries/<slug>/edit',
    view_func=(EditJournalView.as_view(
         'edit',
         template='edit.html',
         form=forms.EditJournalEntryForm)),
    methods=['GET', 'POST'])


class LogoutView(View):

    def dispatch_request(self):
        logout_user()
        flash("You're now logged out.")
        return redirect(url_for('home'))

app.add_url_rule(
    '/logout',
    view_func=LogoutView.as_view('logout'),
    methods=['GET'])
