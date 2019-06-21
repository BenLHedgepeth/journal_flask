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
                    title = journal_entry.title.data,
                    date = journal_entry.data.data,
                    time = journal_entry.time_spent.data,
                    topic = journal_entry.topic_learned.data,
                    resources = journal_entry.resources.data,
                    writer = ForeignKeyField(model=Writer)
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
        entry_tags = (Tag.select()
                    .join(JournalEntryTag)
                    .join(JournalEntry)
                    .where(JournalEntry.slug == slug))

        return (user_entry, entry_tags)


class JournalEntry(ModelConfig):
    title = CharField()
    slug = CharField()
    date = DateField(default=datetime.datetime.now)
    time = TimeField(formats=['%H:%M'])
    topic = TextField()
    resources = TextField(null=True)
    writer_id = ForeignKeyField(model=Writer)



class Tag(ModelConfig):
    name = CharField(unique=True)


class JournalEntryTag(ModelConfig):
    journal_entry = ForeignKeyField(model=JournalEntry)
    journal_tag = ForeignKeyField(model=Tag)





def initialize_tables():
    tables = [Writer, JournalEntry, Tag, JournalEntryTag]
    all_tables_exist = all(database.table_exists(table) == True for table in tables) 

    if all_tables_exist:
        database.drop_tables(tables)
    database.create_tables(tables)        