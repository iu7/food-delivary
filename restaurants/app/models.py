from . import db
from datetime import datetime
from time import strftime
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
import re

class RestaurantConfig:
	NAME_MAX_LEN = 128
	MENU_TITLE_LEN = 64
	CITY_MAX_LEN = 128
	STATION_MAX_LEN = 128
	STREET_MAX_LEN = 256
	COMMENT_MAX_LEN = 512
	CUIS_MAX_LEN = 64
	TELEPHONE_FORMAT = r'((8|\+7)-?)?\(?\d{3}\)?-?\d{1}-?\d{1}-?\d{1}-?\d{1}-?\d{1}-?\d{1}-?\d{1}'
	EMAIL_FORMAT = r'[^@]+@[^@]+\.[^@]+'
	TIME_FORMAT = '%H:%M'
	DTIME_FORMAT = '%Y-%m-%d %H:%M:%S'
	POINTS_PERCENTS = 10.0
	FEES_PERCENTS = 8.0
	OFF_NAME_LEN = 64
	TEL_LEN = 32
	EMAIL_LEN = 64
	INFO_LEN = 256
	MENU_INFO_MAX = 256
	BONUS_PERCENTS = 10.0

class Restaurant(db.Model):
	__tablename__ = 'restaurants'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, nullable=False, unique=True)
	name = db.Column(db.String(RestaurantConfig.NAME_MAX_LEN))
	activated = db.Column(db.Boolean, default=False, nullable=False)
	email = db.Column(db.String(RestaurantConfig.EMAIL_LEN),nullable=False)
	telephone = db.Column(db.String(RestaurantConfig.TEL_LEN), nullable=False)

	address = db.relationship('Address', cascade='all,delete', backref='resaturant')
	menu = db.relationship('Menu', cascade='all,delete', backref='restaurant') 
	attributes = db.relationship('Attributes', cascade='all,delete', backref='restaurant')
	officials = db.relationship('Officials', cascade='all,delete', backref='restaurant')
	cuisines = db.relationship('RestaurantCuisines', cascade='all,delete', backref='restaurant')
	orders = db.relationship('Orders', backref='restaurant')

	def __init__(self, user_id, name, telephone, email):
		self.user_id = user_id
		self.name = name
		self.telephone = telephone
		self.email = email


	@staticmethod
	def get_restaurant_by_preferences(min_payment, online_payment, opened, delivery_time, city, cuisines):
		result = []
		restaurant_list = Restaurant.query.all()
		for restaurant in restaurant_list:
			#TODO if not restaurant.activated: continue
			if restaurant.address[0].city != city: continue
			#print city, cuisines
			if not cuisines: flag = True
			else:
				flag = False
				#print 'restr_cuisines', restaurant.cuisines, 'checked', cuisines
				for cuisine in restaurant.cuisines: flag |= str(cuisine.cuisine_id) in cuisines
			if not flag: continue
			attr = restaurant.attributes[0]
			#print min_payment, online_payment, opened, delivery_time,'\nNEW_LINE_NEW_LINE\n'
			#print attr, flag
			flag = not min_payment or (min_payment and min_payment >= attr.min_payment)
			#print '1', flag
			if flag: flag = not online_payment or online_payment == attr.online_payment
			#print '2', flag
			if flag and opened: flag = restaurant.is_opened()			
			#print '3', flag
			if flag: flag = float(delivery_time) >= attr.delivery_time
			#print '4', flag
			if flag:
				result.append({'restaurant_id':restaurant.id, 'name':restaurant.name,\
					'telephone':restaurant.telephone, 'email':restaurant.email,\
					'attributes' : attr.get_attributes(), 'cuisines':restaurant.get_cuisines()})
		cuisines = Cuisine.get_cuisines(city)['cuisine_list']
		if not cuisines: cuisines = []
		return result, cuisines


	def is_opened(self):
		attr = self.attributes[0]
		days = [attr.monday,attr.tuesday,attr.wednesday,attr.thursday,attr.friday,attr.saturday,attr.sunday]
		flag = days[datetime.today().weekday()]
		if flag:
			flag = attr.open_to != attr.open_from
			if flag:
				now = datetime.now().time()
				fr = attr.open_from.time()
				to = attr.open_to.time()
				if now >= fr:
					if to > fr: flag = now <= to
				elif now <= fr:
					if to < fr: flag = now <= to
					else: flag = False
			else: flag = True
		return flag


	def add_cuisines(self, cuisines):	
		if type(cuisines) is type([]):
			for cuisine in cuisines:
				db.session.add(RestaurantCuisines(self.id, cuisine))
		elif type(cuisines) is type(int()):
			db.session.add(RestaurantCuisines(self.id, cuisines))
		else:
			raise AttributeError('Incorrect cuisines type (list or int is required)')
		db.session.commit()


	def delete_cuisines(self, cuisines):
		if type(cuisines) is type([]):
			for cuisine in cuisines:
				db.session.delete(RestaurantCuisines.query.filter_by(cuisine_id=cuisine).first())
		elif type(cuisines) is type(int()):
			db.session.delete(RestaurantCuisines.query.filter_by(cuisine_id=cuisines).first())
		else:
			raise AttributeError('Incorrect cuisines type (list or int is required)')
		db.session.commit()


	def get_cuisines(self):
		result = []
		for cuisine in self.cuisines:
			result.append({'id':cuisine.cuisine_id, 'title': cuisine.get_cuisine_title()})
			#result.append(cuisine.get_cuisine_title())
		return result


	def get_address_list(self):
		result = []
		for address in self.address:
			result.append(address.get_address())
		return result

	def get_order_list(self):
		result = []
		for order in self.orders:
			result.append(order.get_order())
		return result

	def get_officials_list(self):
		result = []
		for official in self.officials:
			result.append(official.get_officials())
		return result

	def get_menu(self):
		result = []
		try:
			result = self.menu[0].get_menu()
		except Exception, msg:
			result = None
		return result

	def get_attributes(self):
		result = []		
		try:
			result = self.attributes[0].get_attributes()
		except Exception, msg:
			result = None
		return result

	@validates('id')
	def validate_id(self, key, value):
		raise AttributeError('Modification is not allowed')

	@validates('user_id')
	def validate_user_id(self, key, value):
		if Restaurant.query.filter_by(user_id=value).first():
			raise ValueError('Incorrect user_id (user_id already exists)')
		if type(value) is not type(int()) or value <= 0:
			raise ValueError('Incorrect user_id parameter')
		return value

	@validates('name')
	def validate_name(self, key, value):
		restaurant = Restaurant.query.filter_by(name=value).first()
		if restaurant:
			if self != restaurant and restaurant.name == value:
				raise ValueError('Restaurant with the same name already exists')
		if value == '' or value is None:
			raise ValueError('Incorrect name')
		return value

	@validates('activated')
	def validate_activated(self, key, value):
		if type(value) is not type(True):
			raise ValueError('Incorrect activated value')
		return value

	@validates('telephone')
	def validate_telephone(self, key, value):
		if re.match(RestaurantConfig.TELEPHONE_FORMAT, value) is None:
			raise ValueError('Incorrect telephone format')
		return value

	@validates('email')
	def validate_email(self, key, value):
		if re.match(RestaurantConfig.EMAIL_FORMAT, value) is None:
			raise ValueError('Incorrect email format')
		return value

	def __repr__(self):
		return '<Restaurant: id: %s, name: %s, activated: %s, telephone: %s, email: %s' \
		% (str(self.id), str(self.name), str(self.activated), str(self.telephone), str(self.email))

class Officials(db.Model):
	__tablename__ = 'officials'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(RestaurantConfig.OFF_NAME_LEN), nullable=False)
	telephone = db.Column(db.String(RestaurantConfig.TEL_LEN), nullable=False)
	email = db.Column(db.String(RestaurantConfig.EMAIL_LEN),nullable=False)
	info = db.Column(db.String(RestaurantConfig.INFO_LEN))
	restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))

	def __init__(self, restaurant_id, name, telephone, email, info=None):
		self.restaurant_id = restaurant_id
		self.name = name
		self.telephone = telephone
		self.email = email
		if info == None:
			self.info = ''
		else: self.info = info

	def __repr__(self):
		return '<Officials: name: %s, telephone: %s, email: %s, info: %s, restaurant_id: %s' \
			%(str(self.name), str(self.telephone), str(self.email), str(self.info), str(self.restaurant_id))

	def get_officials(self):
		return {'officials' : {'id' : self.id, 'name' : self.name, 'telephone' : self.telephone, \
			'email' : self.email, 'info' : self.info, 'restaurant_id' : self.restaurant_id}}

	@validates('name')
	def validate_name(self, key, value):
		if value == '' or value is None:
			raise ValueError('Incorrect name')
		return value

	@validates('telephone')
	def validate_telephone(self, key, value):
		if re.match(RestaurantConfig.TELEPHONE_FORMAT, value) is None:
			raise ValueError('Incorrect telephone format')
		return value

	@validates('email')
	def validate_email(self, key, value):
		if re.match(RestaurantConfig.EMAIL_FORMAT, value) is None:
			raise ValueError('Incorrect email format')
		return value

	@validates('restaurant_id')
	def validate_restaurant_id(self, key, value):
		if not Restaurant.query.filter_by(id=value).first():
			raise ValueError('Incorrect restaurant_id')
		return value


class Cuisine(db.Model):
	__tablename__ = 'cuisines'
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(RestaurantConfig.CUIS_MAX_LEN), nullable=False, unique=True)
	restaurants = db.relationship('RestaurantCuisines', cascade='all,delete', backref='cuisines')

	def __init__(self, title):
		self.title = title

	@validates('title')
	def validate_title(self, key, value):
		if value is None:
			raise ValueError('Incorrect argument title')
		if Cuisine.query.filter_by(title=value).first() is not None:
			raise ValueError('Cuisine with %s title already exists' % value)
		return value

	@staticmethod
	def insert_cuisines():
		initial_cuisines = ['European', 'Japanese', 'Chinese', \
				'Korean', 'Turkish', 'Russian', 'Asian', \
				'American', 'Italian', 'Different']
		for c in initial_cuisines:
			db.session.add(Cuisine(c))
		db.session.commit()

	@staticmethod
	def get_cuisines(city):
		result = []
		clist = Cuisine.query.all()
		for c in clist:
			result.append({'title' : c.title, 'id': c.id})
		return {'cuisine_list' : result}


	def __repr__(self):
		return '<Cuisine: id: %s, title: %s' % (str(self.id), self.title)


class RestaurantCuisines(db.Model):
	__tablename__ = 'restaurantcuisines'
	id = db.Column(db.Integer, primary_key=True)
	cuisine_id = db.Column(db.Integer, db.ForeignKey('cuisines.id'))
	restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))

	def __init__(self, restaurant_id, cuisine_id):
		self.restaurant_id = restaurant_id
		self.cuisine_id = cuisine_id

	def __repr__(self):
		return '<RestaurantCuisines: restaurant:id: %s, cuisine_id: %s' \
			% (str(self.restaurant_id), str(self.cuisine_id))

	@validates('restaurant_id')
	def validate_restaurant_id(self, key, value):
		if not Restaurant.query.filter_by(id=value).first():
			raise ValueError('Incorrect restaurant_id')
		return value

	@validates('cuisine_id')
	def validate_cuisine_id(self, key, value):
		if not Cuisine.query.filter_by(id=value).first():
			raise ValueError('Incorrect cuisine_id')
		return value

	def get_cuisine_title(self):
		return Cuisine.query.filter_by(id=self.cuisine_id).first().title


class Attributes(db.Model):
	__tablename__ = 'attributes'
	id = db.Column(db.Integer, primary_key=True)
	open_from = db.Column(db.DateTime, nullable=False)
	open_to = db.Column(db.DateTime, nullable=False)
	min_payment = db.Column(db.Float, default=0)
	delivery_payment = db.Column(db.Float, default=0)
	delivery_time = db.Column(db.Float, nullable=False)
	online_payment = db.Column(db.Boolean, default=False, nullable=False)
	restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))
	sunday = db.Column(db.Boolean, default=False, nullable=False)
	monday = db.Column(db.Boolean, default=False, nullable=False)
	tuesday = db.Column(db.Boolean, default=False, nullable=False)
	wednesday= db.Column(db.Boolean, default=False, nullable=False)
	thursday = db.Column(db.Boolean, default=False, nullable=False)
	friday = db.Column(db.Boolean, default=False, nullable=False)
	saturday= db.Column(db.Boolean, default=False, nullable=False)

	def __init__(self, restaurant_id, open_from, open_to, min_paym, del_paym, del_time, wdays):
		self.open_from = open_from
		self.open_to = open_to
		self.min_payment = min_paym
		self.delivery_payment = del_paym
		self.delivery_time = del_time
		self.restaurant_id = restaurant_id
		self.monday = wdays[0]
		self.tuesday = wdays[1]
		self.wednesday= wdays[2]
		self.thursday = wdays[3]
		self.friday = wdays[4]
		self.saturday= wdays[5]
		self.sunday = wdays[6]

	def get_attributes(self):
		return 	{'id' : self.id, 'open_from' : self.open_from.strftime(RestaurantConfig.TIME_FORMAT), \
			'open_to' : self.open_to.strftime(RestaurantConfig.TIME_FORMAT), \
			'min_payment' : self.min_payment, 'delivery_payment' : self.delivery_payment, \
			'delivery_time' : self.delivery_time, 'online_payment' : self.online_payment, \
			'restaurant_id' : self.restaurant_id, 'attribute_id':self.id, \
			'wdays' : [self.monday, self.tuesday, self.wednesday, self.thursday, self.friday, self.saturday,self.sunday]
			}

	@validates('online_payment')
	def validate_online_payment(self, key, value):
		if type(value) is not type(True) and value != 1 and value != 0:
			raise ValueError('Incorrect online_payment value')
		if value == 0: value = False
		elif value == 1: value = True
		return value

	@validates('open_from')
	def validate_open_from(self, key, value):
		try:
			value = datetime.strptime(value, RestaurantConfig.TIME_FORMAT)
		except ValueError, msg:
			raise ValueError(msg)
		return value

	@validates('open_to')
	def validate_open_to(self, key, value):
		try:
			value = datetime.strptime(value, RestaurantConfig.TIME_FORMAT)
		except ValueError, msg:
			raise ValueError(msg)
		return value

	@validates('min_payment')
	def validate_min_payment(self, key, value):
		if value is None  or value < 0:
			raise ValueError('Incorrect min_payment')
		return value

	@validates('delivery_payment')
	def validate_delivery_payment(self, key, value):
		if value is None or  value < 0:
			raise ValueError('Incorrect delivery_payment')
		return value

	@validates('delivery_time')
	def validate_delivery_time(self, key, value):
		if value is None or  value <= 0:
			raise ValueError('Incorrect delivery_time')
		return value

	@validates('restaurant_id')
	def validate_restaurant_id(self, key, value):
		if not Restaurant.query.filter_by(id=value).first():
			raise ValueError('Incorrect restaurant_id')
		return value


	def __repr__(self):
		return '<Attributes: restaurant_id: %s, open_from: %s, open_to: %s, \
			 min_payment: %s, delivery_payment: %s, delivery_time: %s, online_payment: %s' \
			%(str(self.restaurant_id), self.open_from.strftime(RestaurantConfig.TIME_FORMAT), \
			self.open_to.strftime(RestaurantConfig.TIME_FORMAT), \
			str(self.min_payment),str(self.delivery_payment), \
			str(self.delivery_time), str(self.online_payment))


class Menu(db.Model):
	__tablename__ = 'menu'
	id = db.Column(db.Integer, primary_key=True)
	menu_items = db.relationship('MenuItem', cascade='all,delete', backref='menu')
	restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), unique=True)

	def __init__(self, restaurant_id):
		menu = Menu.query.filter_by(restaurant_id=restaurant_id).first()
		if menu:
			raise ValueError('Restaurant menu already exists')
		self.restaurant_id = restaurant_id

	def get_menu(self):
		mitem_list = []
		for menu_item in self.menu_items:
			mitem_list.append(menu_item.get_menu_item())
		return {'menu_id' : self.id, 'menu_items' : mitem_list}

	@validates('restaurant_id')
	def validate_restaurant_id(self, key, value):
		if not Restaurant.query.filter_by(id=value).first():
			raise ValueError('Incorrect restaurant_id')
		if Menu.query.filter_by(restaurant_id=value).first():
			raise ValueError('Restaurant menu already exists')
		return value

	def __repr__(self):
		return '<Menu: id: %s, restaurant_id: %s' % (str(self.id), str(self.restaurant_id))

class MenuItem(db.Model):
	__tablename__ = 'menuitems'
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(RestaurantConfig.MENU_TITLE_LEN))
	price = db.Column(db.Float)
	info = db.Column(db.String(RestaurantConfig.MENU_INFO_MAX))
	menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'))
	#orderlist = db.relationship('OrderList', cascade='all,delete', backref='menuitem')
	bonuses = db.relationship('Bonus', cascade='all,delete', backref='menuitem')

	def __init__(self, menu_id, title, price, info):
		self.title = title
		self.price = price
		self.menu_id = menu_id
		self.info = info

	def get_menu_item(self):
		return {'menu_item_id' : self.id, 'title' : self.title, 'price' : self.price, 'info':self.info}

	@validates('title')
	def validate_title(self, key, value):
		if value is None or value == '':
			raise ValueError('Incorrect title')
		return value

	@validates('price')
	def validate_price(self, key, value):
		if value is None or value < 0:
			raise ValueError('Incorrect price')
		return value

	@validates('menu_id')
	def validate_menu_id(self, key, value):
		if not Menu.query.filter_by(id=value).first():
			raise ValueError('Incorrect menu_id')
		return value

	def __repr__(self):
		return 'MenuItem: id: %s, title: %s, price: %s, menu_id: %s' \
			% (str(self.id), str(self.title), str(self.price), str(self.menu_id))		


class Bonus(db.Model):
	__tablename__ = 'bonuses'
	id = db.Column(db.Integer, primary_key=True)
	menu_item_id = db.Column(db.Integer, db.ForeignKey('menuitems.id'))
	points = db.Column(db.Float, nullable=False)

	def __init__(self, menu_item_id, points):
		self.menu_item_id = menu_item_id
		self.points = points

	def __repr__(self):
		return '<Bonus: id: %s, points: %s' % (str(self.id), str(self.points))

	def get_bonus(self):
		return {'bonus':{'id' : self.id, 'points' : self.points, \
		'menu_item' : MenuItem.query.filter_by(id=self.menu_item_id).first().get_menu_item()}}

	@validates('menu_item_id')
	def validate_menu_item_id(self, key, value):
		if not MenuItem.query.filter_by(id=value).first():
			raise ValueError('Incorrect menu_item_id')
		return value

	@validates('points')
	def validate_points(self, key, value):
		if value is None or type(value) not in [type(float()), type(int())] or value < 0:
			raise ValueError('Incorrects points')
		return value


class CustomerDestination(db.Model):
	__tablename__ = 'destinations'
	id = db.Column(db.Integer, primary_key=True)
	street = db.Column(db.String(256), nullable=False)
	station = db.Column(db.String(256))
	entrance = db.Column(db.String(16))
	passcode = db.Column(db.String(32))
	floor = db.Column(db.Integer)
	order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))


	def get_destination(self):
		return {'id':self.id, 'street':self.street, 'station':self.station, 'entrance':self.entrance, 'floor':self.floor,\
					'passcode':self.passcode}

	def __init__(self, street, station, entrance, passcode, floor, order_id):
		self.street = street
		self.station = station
		self.entrance = entrance
		self.passcode = passcode
		self.order_id = order_id
		if floor: self.floor = int(floor)


	def __repr__(self):
		return '<CustomerDestionation: street: %s, station: %s, entrance: %s, passcode: %s, floor: %s, order_id: %s' %\
			(str(self.street),str(self.station),str(self.entrance),str(self.passcode),str(self.floor), str(self.order_id))

class Customer(db.Model):
	__tablename__ = 'customers'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(RestaurantConfig.NAME_MAX_LEN), nullable=False)
	telephone = db.Column(db.String(RestaurantConfig.TEL_LEN), nullable=False)
	order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))	

	def __init__(self, name, telephone, order_id):
		self.name = name
		self.telephone = telephone
		self.order_id = order_id


	def __repr__(self):
		return '<Customer: name: %s, telephone: %s, order_id: %s' \
			%(self.name, self.telephone, str(self.order_id))

	def get_customer(self):
		return {'id':self.id, 'name':self.name, 'telephone':self.telephone}


class Orders(db.Model):
	__tablename__ = 'orders'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer)
	__date = db.Column('date', db.DateTime(), default=datetime.utcnow())
	confirmed = db.Column(db.Boolean, nullable=False)
	canceled = db.Column(db.Boolean, default=False)
	total = db.Column(db.Float)
	delivery_payment = db.Column(db.Float)
	points = db.Column(db.Float)
	online_payment = db.Column(db.Boolean, default=False)
	restaurant_name = db.Column(db.String(RestaurantConfig.NAME_MAX_LEN), default=None)
	info = db.Column(db.String(RestaurantConfig.INFO_LEN))

	restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))
	customer_list = db.relationship('Customer', cascade='all,delete', backref='order')
	destination_list = db.relationship('CustomerDestination', cascade='all,delete', backref='order')
	order_list = db.relationship('OrderList', cascade='all,delete', backref='order')

	def __init__(self, restaurant_id, restaurant_name, online_payment, total, delivery_payment, user_id):
		self.restaurant_id = restaurant_id
		self.user_id = user_id
		self.restaurant_name = restaurant_name
		self.confirmed = True#TODO change to False
		self.canceled = False
		self.info = ''
		self.delivery_payment = delivery_payment
		self.total = float(total) + float(delivery_payment)
		self.points = round(float(total) / RestaurantConfig.BONUS_PERCENTS, 2)
		self.online_payment = online_payment
		self.__date = datetime.utcnow()

	def __repr__(self):
		return '<Orders: id: %s, restaurant_id: %s, date: %s, confirmed: %s, online_payment: %s, user_id: %s' \
			% (str(self.id), str(self.restaurant_id),\
				self.date, str(self.confirmed), \
				str(self.online_payment), str(self.user_id))

	def get_customer(self):
		return self.customer_list[0].get_customer()

	def get_destination(self):
		return self.destination_list[0].get_destination()
		
	def get_order(self):
		olist = []
		for order in self.order_list:
			olist.append(order.get_order_list())
		return {'order_id' : self.id, 'user_id' : self.user_id, 'confirmed' : self.confirmed, \
			'restaurant_id' : self.restaurant_id, 'restaurant_name' : self.restaurant_name,\
			'date' : self.date, 'canceled':self.canceled, \
			'order_list' : olist, 'online_payment':self.online_payment,'info':self.info, \
			'delivery_payment':self.delivery_payment,'total':self.total, 'points':self.points}


	@validates('confirmed')
	def validate_confirmed(self, key, value):
		if type(value) is not type(True):
			raise ValueError('Incorrect confirmed value')
		return value

	'''@validates('restaurant_id')
	def validate_restaurant_id(self, key, value):
		if not Restaurant.query.filter_by(id=value).first():
			raise ValueError('Incorrect restaurant_id')
		return value'''

	@hybrid_property
	def date(self):
		return self.__date.strftime(RestaurantConfig.DTIME_FORMAT)

	'''@hybrid_property
	def payment(self):
		result = 0
		for order in self.order_list:
			menu_item = MenuItem.query.filter_by(id=order.menu_item_id).first()
			if menu_item:
				result += menu_item.price
		return result

	@hybrid_property
	def points(self):
		payment = self.payment
		if payment == 0:
			result = 0
		else:
			result = self.payment / RestaurantConfig.POINTS_PERCENTS
		return result

	@hybrid_property
	def fees(self):
		payment = self.payment
		if payment == 0:
			result = 0
		else:
			result = self.payment / RestaurantConfig.FEES_PERCENTS
		return result'''

class OrderList(db.Model):
	__tablename__ = 'orderlist'
	id = db.Column(db.Integer, primary_key=True)
	#menu_item_id = db.Column(db.Integer, db.ForeignKey('menuitems.id'))
	title = db.Column(db.String(RestaurantConfig.MENU_TITLE_LEN))
	price = db.Column(db.Float)
	order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))

	def __init__(self, title, price, order_id):
		#self.menu_item_id = menu_item_id
		self.title = title
		self.price = price
		self.order_id = order_id

	def get_order_list(self):
		return {'id' : self.id, 'title': self.title, 'price':self.price}
		#'menu_item' : MenuItem.query.filter_by(id=self.menu_item_id).first().get_menu_item()}}

	@validates('title')
	def validate_title(self, key, value):
		if value is None or value == '':
			raise ValueError('Incorrect title')
		return value

	@validates('price')
	def validate_price(self, key, value):
		if value is None or value < 0:
			raise ValueError('Incorrect price')
		return value

	'''@validates('order_id')
	def validate_order_id(self, key, value):
		if not Orders.query.filter_by(id=value).first():
			raise ValueError('Incorrect order_id')
		return value'''

	def __repr__(self):
		return '<OrderList: id: %s, title: %s, price: %s, order_id: %s' \
			% (str(self.id), str(self.title), str(self.price), str(self.order_id))

class Address(db.Model):
	__tablename__ = 'address'
	id = db.Column(db.Integer, primary_key=True)
	city = db.Column(db.String(RestaurantConfig.CITY_MAX_LEN), nullable=False)
	station = db.Column(db.String(RestaurantConfig.STATION_MAX_LEN))
	street = db.Column(db.String(RestaurantConfig.STREET_MAX_LEN), nullable=False)
	telephone = db.Column(db.String(RestaurantConfig.TEL_LEN), nullable=False)
	restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))

	def __init__(self, restaurant_id, city, street, telephone, station=None):
		self.city = city
		self.street = street
		self.station = station
		self.telephone = telephone
		self.restaurant_id = restaurant_id

	def get_address(self):
		return {'address' : {'id' : self.id, 'city' : self.city, 'station' : self.station, \
			'street' : self.street, 'telephone' : self.telephone, 'restaurant_id' : self.restaurant_id}}

	@validates('restaurant_id')
	def validate_restaurant_id(self, key, value):
		if not Restaurant.query.filter_by(id=value).first():
			raise ValueError('Incorrect restaurant_id')
		return value

	@validates('telephone')
	def validate_telephone(self, key, value):
		if re.match(RestaurantConfig.TELEPHONE_FORMAT, value) is None:
			raise ValueError('Incorrect telephone format')
		return value

	@validates('city')
	def validate_city(self, key, value):
		if value is None or value == '':
			raise ValueError('Incorrect city')
		return value

	@validates('street')
	def validate_street(self, key, value):
		if value is None or value == '':
			raise ValueError('Incorrect street')
		return value

	def __repr__(self):
		return '<Address: restaurant_id: %s, city: %s, street: %s, telephone: %s, station: %s' \
			 % (str(self.restaurant_id), str(self.city), str(self.street), str(self.telephone), str(self.station))


class City(db.Model):
	__tablename__ = 'city'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(RestaurantConfig.CITY_MAX_LEN), nullable=None)

	def __init__(self, name):
		self.name = name
	def __repr__(self):
		return '<City: id: %d, name: %s' % (self.id, self.name)

	@validates('name')
	def validate_name(self, key, value):
		if any(v.isdigit() for v in value):
			raise ValueError('Incorrect city name')
		return value

	@staticmethod
	def get_real_cities():
		result = []
		cities = City.query.all()
		for city in cities:
			if Address.query.filter_by(city=city.name).first():
				result.append(city.name)
		return {'cities_list' : result}


	@staticmethod
	def get_cities():
		result = []
		cities = City.query.all()
		for city in cities:
			result.append(city.name)
		return {'cities_list' : result}

	@staticmethod
	def insert_cities():
		initial_cities = ['London', 'New-York', 'Las Vsegas', 'Miami']
		for city in initial_cities:
			db.session.add(City(city))
		db.session.commit()


