import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
        ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = ' <flasky@example.com>'
    SYSTEM_ADMIN = "admin"
    SYSTEM_ADMIN_NAME = "Владимир Пайор"
    SYSTEM_ADMIN_PASSWORD = "Admin@123"
    SSL_REDIRECT = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    FLASKY_SLOW_DB_QUERY_TIME = 0.5


    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    LOGIN_VIEW = "http://localhost:5000/auth/login"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:{11111111}@localhost/foods?charset=utf8mb4"
    APPLICATION_ROOT = "/mining_foods"


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:{11111111}@localhost/foods_test?charset=utf8mb4"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI =  "mysql+pymysql://minecite:DBspmi-20@localhost/foods"
    LOGIN_VIEW = "https://digital.spmi.ru/mining_foods/auth/login"
    SERVER_NAME = "https://digital.spmi.ru/"
    PREFERRED_URL_SCHEME = "https"
    APPLICATION_ROOT = "/mining_foods"

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the administrators
        import logging
        logging.basicConfig(filename='food.log', level=logging.DEBUG)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}