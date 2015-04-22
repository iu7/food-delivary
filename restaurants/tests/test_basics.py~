import unittest
from flask import current_app
from app import create_app, db
from app.models import Client, History, Address

import time
from datetime import datetime


class BasicsTestCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	def test_app_exists(self):
		self.assertFalse(current_app is None)

	def test_app_is_testing(self):
		self.assertTrue(current_app.config['TESTING'])

	def test_client_bad_init(self):
		c = Client('Alice', 'alice@gmail.com', '+79099946885')
		c.password = 'helloworld'
		db.session.add(c)
		flag = False
		try:
			db.session.commit()
		except:
			flag = True
		self.assertTrue(flag)

	def test_client_good_init(self):
		c = Client('Alice', 'alice@gmail.com', '+79099946885')
		c.password = 'helloworld'
		db.session.add(c)
		self.assertIsNone(db.session.commit())

	def test_client_unique(self):
		c1 = Client('Alice', 'alice@gmail.com', '+79099946885')
		c2 = Client('Alice', 'alice@gmail.com', '+79099946885')
		c1.password = 'helloworld'
		c2.password = 'helloworld'
		db.session.add(c1)
		db.session.add(c2)
		flag = False
		try:
			db.session.commit()
		except:
			flag = True
		self.assertTrue(flag)

	def test_password_getter(self):
		c = Client('Alice', 'alice@gmail.com', '+79099946885')
		with self.assertRaises(AttributeError):
			c.password

	












