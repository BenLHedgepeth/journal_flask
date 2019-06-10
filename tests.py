
import faker
import unittest
import models

from flask import url_for

import app

# configure the testing environment
app.app.config.from_object('instance.config.TestingConfig')
# initialize the database         
models.database.init(app.app.config['DATABASE'])

app_models = (models.Writer, models.JournalEntry, models.Tag)


class TestCaseConfig(unittest.TestCase):

    test_login_data = {
        'user_name' : 'user1',
        'password' : 'password'
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
                self.assertIn(b"Registration failed.", response.data)

class LoginViewTestCase(TestCaseConfig):
    def test_login_user_registered(self):
        TestCaseConfig.writer_generator(self)
        with app.app.app_context():
            with app.app.test_client() as client:
                response = client.post(
                    url_for('login'),
                    data=self.test_login_data,
                    follow_redirects=True
                 )

                self.assertIn(b"Login Successful!", response.data)

    # def test_login_user_not_registered(self):
    #         TestCaseConfig.writer_generator(self, 2)
    #         with app.app.app_context():
    #             with app.app.test_client() as client:
    #                 response = client.post(
    #                     url_for('login'),
    #                     data=self.test_login_data,
    #                     follow_redirects=True
    #                  )

    #                 self.assertEqual(response.status_code, 302)     



if __name__ == '__main__':
    unittest.main()