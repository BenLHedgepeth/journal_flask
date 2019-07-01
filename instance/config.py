
import os

from secrets import token_hex


class BaseConfig:
    DATABASE = 'development.db'
    SECRET_KEY = 'Shhhh!!'
    DEBUG = False
    TESTING = False

    @staticmethod
    def setup_app_config():
        environment = os.environ.get('FLASK_ENV')
        if environment == 'development':
            return 'instance.config.DevelopmentConfig'
        return 'instance.config.ProductionConfig'


class ProductionConfig(BaseConfig):
    DATABASE = 'production.db'
    SECRET_KEY = token_hex()


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    SERVER_NAME = "app.dev:5000"
    WTF_CSRF_ENABLED = False
    DATABASE = 'testing.db'
    TESTING = True
