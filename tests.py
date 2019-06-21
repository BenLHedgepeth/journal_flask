
import faker
import unittest
import models

from flask import url_for
from flask_login import current_user

import app

# configure the testing environment
app.app.config.from_object('instance.config.TestingConfig')
# initialize the database         
models.database.init(app.app.config['DATABASE'])

app_models = (models.Writer, models.JournalEntry, models.Tag, models.JournalEntryTag)


class TestCaseConfig(unittest.TestCase):

    test_valid_login_data = {
        'user_name' : 'user1',
        'password' : 'password'
    }

    test_invalid_login_password = {
        'user_name' : 'user1',
        'password' : 'secret'
    }

    test_writer = {
        'user_name' : 'user1',
        'email' : 'user1@email.com',
        'password' : 'password',
    }

    test_register_data = {
        'user_name' : 'user1',
        'email' : 'user1@email.com',
        'password' : 'password',
        'confirm' : 'password'
    }

    test_entry_data = {
        'title' : "Title",
        'slug' : "Slug",
        'date' : "Date",
        'time' : 10,
        'topic' : "Topic",
        'resources' : "Resource",
        'tags' : ['tag1', 'tag2'],
        'writer_id' : test_writer['user_name']
    }

    def writer_generator(self, num=1):
        for i in range(1, num + 1):
            models.Writer.create_writer(
                 user_name=f'user{i}',
                 email=f'user{i}@email.com', 
                 password='password'
             )
        return models.Writer.select()

    def setUp(self):

       with models.database:
            models.database.bind(app_models)
            models.database.create_tables(app_models)

    def tearDown(self):
        with models.database:
            models.database.drop_tables(app_models)
   
        

class CreateWriterTestCase(TestCaseConfig):

    def test_create_writer(self):
        '''Testing entity instance with new data'''
        test_writers = self.writer_generator(1)

        self.assertIsInstance(test_writers.get(), models.Writer)
        self.assertEqual(test_writers.count(), 1)

    def test_create_writer_already_exists(self):
        '''Testing table integrity with unique constraints'''
        with self.assertRaises(ValueError):
            for _ in range(2):
                models.Writer.create_writer(**self.test_writer)


class RegisterViewTestCase(TestCaseConfig):

    def test_register_new_user(self):
        with app.app.app_context():
            with app.app.test_client() as client:
             response = client.post(
                     url_for('register'), 
                     data=self.test_register_data,
                     follow_redirects=True
                 )
             self.assertIn(b"Your account has been created!", response.data)

    def test_register_existing_user(self):

       models.Writer.create_writer(**self.test_writer)

       with app.app.app_context():
            with app.app.test_client() as client:
                response = client.post(
                        url_for('register'), 
                        data=self.test_register_data,
                        follow_redirects=True
                    )
                self.assertIn(b"An active account exists.", response.data)


class LoginViewTestCase(TestCaseConfig):

    def test_login_registered(self):

        TestCaseConfig.writer_generator(self)
        with app.app.app_context():
            with app.app.test_client() as client:
                response = client.post(
                    url_for('login'),
                    data=self.test_valid_login_data,
                    follow_redirects=True
                 )
                self.assertIn(b"Login Successful!", response.data)
                self.assertEqual(current_user.user_name, 'user1')
                 

    def test_login_not_registered(self):

        with app.app.app_context():
            with app.app.test_client() as client:
                response = client.post(
                    url_for('login'),
                    data=self.test_valid_login_data,
                    follow_redirects=True
                 )
                self.assertIn(b"That account does not exist.", response.data) 

    def test_login_wrong_password(self):

        TestCaseConfig.writer_generator(self)
        with app.app.app_context():
            with app.app.test_client() as client:
                response = client.post(
                    url_for('login'),
                    data=self.test_invalid_login_password,
                    follow_redirects=True
                 )
                self.assertIn(b"Invalid username and/or password", response.data)

class NewEntryTestCase(unittest.TestCase):

    def test_write_entry(self):
        TestCaseConfig.writer_generator(self)
        with app.app.app_context():
            with app.app.test_client() as client:
                client.post(
                    url_for('login'),
                    data=self.test_valid_login_data
                 )
                # response = client.post(
                #     url_for('add_entry'),
                #     data=self.test_entry_data
                #  )

                # self.assertEqual(current_user, 'user1')




if __name__ == '__main__':
    unittest.main()