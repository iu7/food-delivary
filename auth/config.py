import os
basedir = os.path.abspath(os.path.dirname(__file__))
from datetime import timedelta

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(64)
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	MAIL_SUBJECT_PREFIX = 'Food Delivery'
	MAIL_SENDER = 'Food Delivery Manager'
	MAIL_ADMIN = os.environ.get('FLASKY_ADMIN') or 'food.delivery.ds@gmail.com'

	SESSION_LIFETIME = timedelta(seconds=15)
	REDIS_HOST = 'localhost'
	REDIS_PORT = 6379
	REDIS_DB = 0

	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(Config):
	DEBUG = True
	MAIL_SERVER = 'smtp.googlemail.com'
	MAIL_PORT = 587
	MAIL_USE_TLS = True
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'food.delivery.ds@gmail.com'#'distributed.systems.iu7@gmail.com'
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

class ProductionConfig(Config):
	DEBUG = False
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'data.sqlite')

config = {
	'development' : DevelopmentConfig,
	'testing' : TestingConfig,
	'production' : ProductionConfig,

	'default' : DevelopmentConfig
}
