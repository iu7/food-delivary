import os
import configparser
settings = configparser.ConfigParser()
settings.read('settings.cfg')
basedir = os.path.abspath(os.path.dirname(__file__))
from datetime import datetime, timedelta

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(64)
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	FLASKY_MAIN_SUBJECT_PREFIX = 'Flask app'
	FLASKY_MAIL_SENDER = 'Flask admin'
	FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
	LOGIC_URL = settings.get('LogicBackend', 'URL') + settings.get('LogicBackend', 'PORT')

	#PERMANENT_SESSION_LIFETIME = timedelta(seconds=2)
	#SESSION_LIFETIME = timedelta(seconds=2)

	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(Config):
	DEBUG = True
	MAIL_SERVER = 'smtp.googlemail.com'
	MAIL_PORT = 587
	MAIL_USE_TLS = True
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'distributed.systems.iu7@gmail.com'
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'data.sqlite')

config = {
	'development' : DevelopmentConfig,
	'testing' : TestingConfig,
	'production' : ProductionConfig,

	'default' : DevelopmentConfig
}
