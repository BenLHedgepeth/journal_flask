import datetime

from peewee import *

from flask_login import UserMixin

from flask_bcrypt import generate_password_hash

from slugify import slugify

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
        with database.transaction():
            try:
                Writer.create(
                    user_name=user_name,
                    email=email,
                    password=generate_password_hash(password)
                )

            except IntegrityError:
                raise ValueError
            else:
                pass

    def write_entry(self, entry):
        with database.transaction():
            try:
                JournalEntry.create(
                    title=entry.title.data,
                    slug=slugify(entry.title.data),
                    date=entry.date.data,
                    time=entry.time.data,
                    topic=entry.topic.data,
                    resources=entry.resources.data,
                    writer=entry.writer
                )
            except IntegrityError:
                raise ValueError
            else:
                pass

    def retrieve_entry(self, slug):
        user_entry = JournalEntry.get_or_none(
                JournalEntry.slug == slug
            )
        if not user_entry:
            return False
        entry_tags = (
            Tag.select()
            .join(JournalEntryTag)
            .join(JournalEntry)
            .where(JournalEntry.id == user_entry.id))

        return (user_entry, entry_tags)


class JournalEntry(ModelConfig):
    title = CharField(unique=True)
    slug = CharField()
    date = DateField(default=datetime.datetime.now)
    time = TimeField(formats=['%H:%M'])
    topic = TextField()
    resources = TextField(null=True)
    writer = ForeignKeyField(model=Writer)


class Tag(ModelConfig):
    name = CharField(unique=True)


class JournalEntryTag(ModelConfig):
    journal_entry = ForeignKeyField(model=JournalEntry)
    journal_tag = ForeignKeyField(model=Tag)


def initialize_tables():
    tables = [Writer, JournalEntry, Tag, JournalEntryTag]
    all_tables_exist = all(database.table_exists(table) for table in tables)

    if all_tables_exist:
        database.drop_tables(tables)
    database.create_tables(tables)