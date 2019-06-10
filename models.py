import datetime


from peewee import *
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash
import app

database = SqliteDatabase(None)

class ModelConfig(Model):
    class Meta:
        database = database


class Writer(UserMixin, ModelConfig):
    user_name = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField()

    def __str__(self):
        return f'{self.user_name}'

    @classmethod
    def create_writer(cls, user_name, email, password):
        app.app.logger.debug("Registering a user here.")
        with database.transaction():
            try:
                Writer.create(
                    user_name=user_name,
                    email=email,
                    password=generate_password_hash(password).decode("utf-8")
                )

            except IntegrityError:
                raise ValueError
            else:
                me = Writer.get(Writer.user_name == 'You')
                app.app.logger.debug(f"Password hash assigned to user: {me.password}")


    def write_entry(self, journal_entry):
        with database.transaction():
            try:
                JournalEntry.create(
                    title = journal_entry.title.data,
                    date = journal_entry.data.data,
                    time_spent = journal_entry.time_spent.data,
                    topic_learned = journal_entry.topic_learned.data,
                    resources = journal_entry.resources.data,
                    writer = ForeignKeyField(model=Writer)
                )
            except IntegrityError:
                raise ValueError
            else:
                pass

class JournalEntry(ModelConfig):
    title = CharField()
    date = DateField(default=datetime.datetime.now)
    time_spent = TimeField(formats=['%H:%M'])
    topic_learned = TextField()
    resources = TextField(null=True)
    writer = ForeignKeyField(model=Writer)


class Tag(ModelConfig):
    tag_link = CharField(unique=True)
    logged_entry = ForeignKeyField(model=JournalEntry)

def initialize_tables():
    tables = [Writer, JournalEntry, Tag]
    all_tables_exist = all(database.table_exists(table) == True for table in tables) 

    if all_tables_exist:
        database.drop_tables(tables)
    database.create_tables(tables)        