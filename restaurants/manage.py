#!/usr/bin/env python

import os
from app import create_app, db
from flask.ext.script import Manager, Shell, Server
from flask.ext.migrate import Migrate, MigrateCommand
from app.models import Restaurant, Attributes, Cuisine, Menu, Customer, CustomerDestination,\
		MenuItem, Orders, OrderList, Address, Officials, Bonus, RestaurantCuisines, City

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
	return dict(app=app, db=db, Restaurant=Restaurant, \
			 Attributes=Attributes, Cuisine=Cuisine, Menu=Menu, MenuItem=MenuItem, \
			Orders=Orders, OrderList=OrderList, Address=Address, Customer=Customer, CustomerDestination=CustomerDestination,\
			Officials=Officials, Bonus=Bonus,RestaurantCuisines=RestaurantCuisines, City=City)

@manager.command
def test():
	import unittest
	tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity=2).run(tests)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
manager.add_command('runserver', Server(host='0.0.0.0',port='5003'))

if __name__ == '__main__':
	manager.run()
