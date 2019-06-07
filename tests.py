
import faker
import unittest
import models

from flask import url_for, has_app_context

import app

# configure the testing environment
app.app.config.from_object('instance.config.TestingConfig')
# initialize the database         
models.database.init(app.app.config['DATABASE'])


class TestCaseConfig(unittest.TestCase):
    app_models = [models.Writer, models.JournalEntry, models.Tag]
    models.database.bind(app_models)

    def setUp(self):   
        with models.database:
            models.database.create_tables(self.app_models)
        print(f'Tables created. Database is now closed {models.database.is_closed()}')


    def tearDown(self):
        with models.database:
            models.database.drop_tables(self.app_models)
   
        

class CreateWriterTestCase(TestCaseConfig):

    @classmethod
    def setUpClass(cls):
        cls.test_writer = {
            'user_name' : 'user1',
            'email' : 'user1email.com',
            'password' : app.bcrypt.generate_password_hash('password')
        }

    def test_create_writer(self):
        '''Testing entity instance with new data'''
        models.Writer.create_writer(**self.test_writer)
        self.writer = models.Writer.select().get()
        self.writer_entity_instances = models.Writer.select().count()

        self.assertIsInstance(self.writer, models.Writer)
        self.assertEqual(self.writer_entity_instances, 1)


    def test_create_writer_already_exists(self):
        '''Testing table integrity with unique constraints'''
        with self.assertRaises(ValueError):
            for _ in range(2):
                models.Writer.create_writer(**self.test_writer)


class RegisterViewTestCase(TestCaseConfig):

    @classmethod
    def setUpClass(cls):

        cls.user_data = {
            'user_name' : "user1",
            'email' : 'user1@email.com',
            'password' : 'password'
        }

    def test_register_new_user(self):
        print("Open the app context")
        with app.app.app_context():
            print(f"Is the app context open: {has_app_context()}")
            models.database.connect()
            print(f'The database is now open for the request context: {models.database.is_closed()}')
            print("Enter request context")
            with app.app.test_client() as client:
                response = client.post(
                        url_for('register'), 
                        data=self.user_data,
                        follow_redirects=False
                    )

                self.assertEqual(response.status_code, 302)
                self.assertIn(b"Your account has been created!", response.data)


if __name__ == '__main__':
    unittest.main()