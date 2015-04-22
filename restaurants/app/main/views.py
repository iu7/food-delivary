from datetime import datetime
from . import main
from flask import request, jsonify
from .. import db
from .. exceptions import UException

from .. models import Restaurant, Attributes, Cuisine, Menu, \
			MenuItem, Orders, OrderList, Address, Officials, Bonus, RestaurantCuisines, City

@main.route('/')
def index():
	return 'restaurant service'

@main.route('/restaurant/register', methods=['POST'])
def restaurant_register():
	name = request.json.get('name')
	email = request.json.get('email')
	telephone = request.json.get('telephone')
	user_id = request.json.get('user_id')
	if name is None or email is None or telephone is None or user_id is None:
		raise UException('Incorrect request: incorrect parameters')
	try:
		restaurant = Restaurant(user_id, name, telephone, email)
		db.session.add(restaurant)
		db.session.commit()
		menu = Menu(restaurant.id)
		db.session.add(menu)
		db.session.commit()
	except ValueError as error:
		raise UException(message=error.message)
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500, payload=exc.message)
	return jsonify(status='created', restaurant_id=restaurant.id, user_id=user_id), 201

@main.route('/restaurant/<int:user_id>/info')
def restaurant_info(user_id):
	restaurant = Restaurant.query.filter_by(user_id=user_id).first()
	if not restaurant:
		raise UException('Incorrect user_id')
	return jsonify(name=restaurant.name, order_email=restaurant.email, activated=restaurant.activated,\
				telephone=restaurant.telephone, restaurant_id=restaurant.id)

@main.route('/restaurant/<int:restaurant_id>/address/list')
def restaurant_address_list(restaurant_id):
	restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
	if not restaurant:
		raise UException('Incorrect restaurant_id')
	return jsonify(restaurant_id=restaurant.id, restaurant_address_list=restaurant.get_address_list())

@main.route('/restaurant/<int:restaurant_id>/order/list')
def restaurant_order_list(restaurant_id):
	restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
	if not restaurant:
		raise UException('Incorrect restaurant_id')
	return jsonify(restaurant_id=restaurant.id, restaurant_address_list=restaurant.get_order_list())

@main.route('/restaurant/<int:restaurant_id>/officials/list')
def restaurant_officials_list(restaurant_id):
	restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
	if not restaurant:
		raise UException('Incorrect restaurant_id')
	return jsonify(restaurant_id=restaurant.id, officials_list=restaurant.get_officials_list())

@main.route('/restaurant/<int:restaurant_id>/menu')
def restaurant_menu(restaurant_id):
	restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
	if not restaurant:
		raise UException('Incorrect restaurant_id')
	return jsonify(restaurant_id=restaurant.id, menu=restaurant.get_menu())

@main.route('/restaurant/<int:restaurant_id>/attributes')
def restaurant_attributes(restaurant_id):
	restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
	if not restaurant:
		raise UException('Incorrect restaurant_id')
	return jsonify(restaurant_id=restaurant.id, attributes=restaurant.get_attributes(),cuisines=restaurant.get_cuisines())

@main.route('/restaurant/<int:restaurant_id>/cuisine/list')
def restaurant_cuisine_list(restaurant_id):
	restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
	if not restaurant:
		raise UException('Incorrect restaurant_id')
	return jsonify(restaurant_id=restaurant.id, cuisine_list=restaurant.get_cuisines())

@main.route('/restaurant/<int:restaurant_id>/cuisines/add', methods=['POST'])
def restaurant_cuisine_add(restaurant_id):
	restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
	if not restaurant:
		raise UException('Incorrect restaurant_id')
	cuisines = request.json.get('cuisines')
	try:
		restaurant.add_cuisines(cuisines)
	except (ValueError, AttributeError) as error:
		raise UException(message=error.message)
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500, payload=exc.message)
	return jsonify(status='added', restaurant_id=restaurant.id)

@main.route('/restaurant/<int:restaurant_id>/update', methods=['PUT'])
def restaurant_update(restaurant_id):
	restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
	if not restaurant:
		raise UException('Incorrect restaurant_id')
	email = request.json.get('email')
	telephone = request.json.get('telephone')
	name = request.json.get('name')
	try:
		if name: restaurant.name = name
		if email: restaurant.email = email
		if telephone: restaurant.telephone = telephone
		db.session.commit()
	except ValueError as error:
		raise UException(message=error.message)
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500, payload=exc.message)
	return jsonify(status='updated',restaurant_id=restaurant.id)

@main.route('/restaurant/<int:restaurant_id>/delete', methods=['DELETE'])
def restaurant_delete(restaurant_id):
	restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
	if not restaurant:
		raise UException('Incorrect restaurant_id')
	try:
		db.session.delete(restaurant)
		db.session.commit()
	except:
		raise UException(message='Unexpected server exception', status_code=500)
	return jsonify(status='deleted')

@main.route('/restaurant/<int:restaurant_id>/officials/create', methods=['POST'])
def officials_create(restaurant_id):
	restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
	if not restaurant:
		raise UException('Incorrect restaurant_id')
	name = request.json.get('name')
	telephone = request.json.get('telephone')
	email = request.json.get('email')
	info = request.json.get('info')
	if name is None or telephone is None or email is None:
		raise UException('Incorrect parameters')
	try:
		officials = Officials(restaurant_id, name, telephone, email, info)
		db.session.add(officials)
		db.session.commit()
	except ValueError as error:
		raise UException(message=error.message)
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500, payload=exc.message)
	return jsonify(status='created', officials_id=officials.id), 201

@main.route('/restaurant/officials/<int:officials_id>/update', methods=['PUT'])
def officials_update(officials_id):
	officials = Officials.query.filter_by(id=officials_id).first()
	if not officials:
		raise UException('Incorrect officials_id')
	name = request.json.get('name')
	telephone = request.json.get('telephone')
	email = request.json.get('email')
	info = request.json.get('info')
	if name is None or telephone is None or email is None:
		raise UException('Incorrect parameters')
	try:
		if name: officials.name = name
		if email: officials.email = email
		if telephone: officials.telephone = telephone
		if info or info =='': officials.info = info
		db.session.commit()
	except ValueError as error:
		raise UException(message=error.message)
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500, payload=exc.message)
	return jsonify(status='updated', officials_id=officials.id)

@main.route('/restaurant/officials/<int:officials_id>/delete', methods=['DELETE'])
def officials_delete(officials_id):
	officials = Officials.query.filter_by(id=officials_id).first()
	if not officials:
		raise UException('Incorrect officials_id')
	try:
		db.session.delete(officials)
		db.session.commit()
	except:
		raise UException(message='Unexpected server exception', status_code=500)
	return jsonify(status='deleted')

@main.route('/restaurant/cuisine/list')
def cuisine_list():
	return jsonify(Cuisine.get_cuisines())

@main.route('/restaurant/cuisine/create', methods=['POST'])
def cuisine_create():
	title = request.json.get('title')
	if title is None:
		raise UException('Incorrect parameters')
	try:
		cuisine = Cuisine(title)
		db.session.add(cuisine)
		db.session.commit()
	except ValueError as error:
		raise UException(message=error.message)
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500, payload=exc.message)
	return jsonify(status='created', cuisine_id=cuisine.id), 201

@main.route('/restaurant/cuisine/<int:cuisine_id>/delete', methods=['DELETE'])
def cuisine_delete(cuisine_id):
	cuisine = Cuisine.query.filter_by(id=cuisine_id).first()
	if not cuisine:
		raise UException('Incorrect cuisine_id')
	try:
		db.session.delete(cuisine)
		db.session.commit()
	except:
		raise UException(message='Unexpected server exception', status_code=500)
	return jsonify(status='deleted')

@main.route('/restaurant/cuisine/list/<int:restaurant_id>/delete', methods=['DELETE'])
def cuisine_list_delete(restaurant_id):
	restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
	cuisines = request.json.get('cuisines')
	if not restaurant:
		raise UException('Incorrect restaurant_id')
	try:
		restaurant.delete_cuisines(cuisines)
	except:
		raise UException(message='Unexpected server exception', status_code=500)
	return jsonify(status='deleted')


@main.route('/restaurant/<int:restaurant_id>/attributes/create', methods=['POST'])
def attributes_create(restaurant_id):
	restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
	if not restaurant:
		raise UException('Incorrect restaurant id')
	open_from = request.json.get('open_from')
	open_to = request.json.get('open_to')
	min_payment = request.json.get('min_payment')
	delivery_payment = request.json.get('delivery_payment')
	delivery_time = request.json.get('delivery_time')
	online_payment  = request.json.get('online_payment')
	wdays = request.json.get('wdays')
	try:
		attributes = Attributes(restaurant.id, open_from, open_to, \
				min_payment, delivery_payment, delivery_time, wdays)
		if online_payment is not None: attributes.online_payment = online_payment
		db.session.add(attributes)
		db.session.commit()
	except ValueError as error:
		raise UException(message=error.message)
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500)
	return jsonify(status='created', restaurant_id=restaurant.id, attributes_id=attributes.id), 201

@main.route('/restaurant/attributes/<int:attributes_id>/delete', methods=['DELETE'])
def attributes_delete(attributes_id):
	attributes = Attributes.query.filter_by(id=attributes_id).first()
	if not attributes:
		raise UException('Incorrect attributes_id')
	try:
		db.session.delete(attributes)
		db.session.commit()
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500)
	return jsonify(status='deleted')

@main.route('/restaurant/attributes/<int:attributes_id>/update', methods=['PUT'])
def attributes_update(attributes_id):
	attributes = Attributes.query.filter_by(id=attributes_id).first()
	if not attributes:
		raise UException('Incorrect attributes_id')
	open_from = request.json.get('open_from')
	open_to = request.json.get('open_to')
	min_payment = request.json.get('min_payment')
	delivery_payment = request.json.get('delivery_payment')
	delivery_time = request.json.get('delivery_time')
	online_payment  = request.json.get('online_payment')
	monday = request.json.get('wdays')[0]
	tuesday = request.json.get('wdays')[1]
	wednesday = request.json.get('wdays')[2]
	thursday = request.json.get('wdays')[3]
	friday = request.json.get('wdays')[4]
	saturday = request.json.get('wdays')[5]
	sunday = request.json.get('wdays')[6]
	try:
		if open_from: attributes.open_from = open_from
		if open_to: attributes.open_to = open_to
		if min_payment: attributes.min_payment = min_payment
		if delivery_payment: attributes.delivery_payment = delivery_payment
		if delivery_time: attributes.delivery_time = delivery_time
		if online_payment is not None: attributes.online_payment = online_payment
		if monday is not None : attributes.monday = monday
		if tuesday is not None : attributes.tuesday = tuesday
		if wednesday is not None : attributes.wednesday = wednesday
		if thursday is not None : attributes.thursday = thursday
		if friday is not None : attributes.friday = friday
		if saturday is not None : attributes.saturday = saturday
		if sunday is not None : attributes.sunday = sunday
		db.session.commit()
	except ValueError as error:
		raise UException(message=error.message)
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500)
	return jsonify(status='updated', attributes_id=attributes.id)

@main.route('/restaurant/<int:restaurant_id>/bonus/create', methods=['POST'])
def bonus_create(restaurant_id):
	restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
	if not restaurant:
		raise UException('Incorrect restaurant_id')
	menu_item_id = request.json.get('menu_item_id')
	points = request.json.get('points')
	if not points or not menu_item_id:
		raise UException('Incorrect parameters')
	try:
		bonus = Bonus(menu_item_id, points)
		db.session.add(bonus)
		db.session.commit()
	except ValueError as error:
		raise UException(message=error.message)
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500)
	return jsonify(status='created', restaurant_id=restaurant.id, bonus_id=bonus.id), 201

@main.route('/restaurant/bonus/<int:bonus_id>/delete', methods=['DELETE'])
def bonus_delete(bonus_id):
	bonus = Bonus.query.filter_by(id=bonus_id).first()
	if not bonus:
		raise UException('Incorrect bonus_id')
	try:
		db.session.delete(bonus)
		db.session.commit()
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500)
	return jsonify(status='deleted')

@main.route('/restaurant/<int:restaurant_id>/menu/create')
def restaurant_menu_create(restaurant_id):
	try:
		menu = Menu(restaurant_id)
		db.session.add(menu)
		db.session.commit()
	except ValueError as error:
		raise UException(message=error.message)
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500)
	return jsonify(status='created', restaurant_id=restaurant_id, menu_id=menu.id), 201

@main.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['DELETE'])
def restaurant_menu_delete(restaurant_id, menu_id):
	menu = Menu.query.filter_by(id=menu_id).first()
	if not menu:
		raise UException('Incorrect menu_id')
	if menu.restaurant_id != restaurant_id:
		raise UException('Incorrect restaurant menu')
	try:
		db.session.delete(menu)
		db.session.commit()
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500)
	return jsonify(status='deleted')

@main.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/menu_item/create', methods=['POST'])
def restaurant_menu_item_create(restaurant_id, menu_id):
	menu = Menu.query.filter_by(id=menu_id).first()
	if not menu:
		raise UException('Incorrect menu_id')
	if menu.restaurant_id != restaurant_id:
		raise UException('Incorrect restaurant menu')
	title = request.json.get('title')
	price = request.json.get('price')
	info = request.json.get('info')
	try:
		mitem = MenuItem(menu_id, title, price, info)
		db.session.add(mitem)
		db.session.commit()
	except ValueError as error:
		raise UException(message=error.message)
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500)
	return jsonify(status='created', menu_id=menu.id, menu_item_id=mitem.id), 201


@main.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/menu_item/<int:menu_item_id>/update', methods=['PUT'])
def restaurant_menu_item_update(restaurant_id, menu_id, menu_item_id):
	menu = Menu.query.filter_by(id=menu_id).first()
	if not menu:
		raise UException('Incorrect menu_id')
	if menu.restaurant_id != restaurant_id:
		raise UException('Incorrect restaurant menu')
	mitem = MenuItem.query.filter_by(id=menu_item_id).first()
	if not mitem or mitem.menu_id != menu.id:
		raise UException('Incorrect menu_item_id')
	title = request.json.get('title')
	price = request.json.get('price')
	info = request.json.get('info')
	try:
		if title: mitem.title = title
		if price: mitem.price = price
		if info is not None or info == '': mitem.info = info
		db.session.commit()
	except ValueError as error:
		raise UException(message=error.message)
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500)
	return jsonify(status='updated')

@main.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/menu_item/<int:menu_item_id>/delete', methods=['DELETE'])
def restaurant_menu_item_delete(restaurant_id, menu_id, menu_item_id):
	menu = Menu.query.filter_by(id=menu_id).first()
	if not menu:
		raise UException('Incorrect menu_id')
	if menu.restaurant_id != restaurant_id:
		raise UException('Incorrect restaurant menu')
	mitem = MenuItem.query.filter_by(id=menu_item_id).first()
	if not mitem or mitem.menu_id != menu.id:
		raise UException('Incorrect menu_item_id')
	try:
		db.session.delete(mitem)
		db.session.commit()
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500)
	return jsonify(status='deleted')


@main.route('/restaurant/<int:restaurant_id>/orders/create', methods=['POST'])
def odrers_create(restaurant_id):
	restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
	if not restaurant:
		raise UException('Incorrect restaurant_id')
	user_id = request.json.get('user_id')
	try:
		order = Orders(user_id, restaurant_id)
		db.session.add(order)
		db.session.commit()
	except ValueError as error:
		raise UException(message=error.message)
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500)
	return jsonify(status='created', order_id=order.id, user_id=user_id, restaurant_id=restaurant_id), 201


@main.route('/restaurant/<int:restaurant_id>/orders/<int:order_id>/update', methods=['PUT'])
def orders_update(restaurant_id, order_id):
	restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
	order = Orders.query.filter_by(id=order_id).first()
	if not restaurant or not order or order.restaurant_id != restaurant.id:
		raise UException('Incorrect restaurant_id or order_id')
	confirmed = request.json.get('confirmed')
	if confirmed is None:
		raise UException('Incorrect request')
	try:
		order.confirmed = bool(confirmed)
		db.session.commit()
	except ValueError as error:
		raise UException(message=error.message)
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500)
	return jsonify(status='updated')


@main.route('/restaurant/<int:restaurant_id>/orders/<int:order_id>/delete', methods=['DELETE'])
def orders_delete(restaurant_id, order_id):
	order = Orders.query.filter_by(id=order_id).first()
	if not order or order.restaurant_id != restaurant_id:
		raise UException('Incorrect restaurant_id or order_id')
	try:
		db.session.delete(order)
		db.session.commit()
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500)
	return jsonify(status='deleted')

@main.route('/restaurant/orders/<int:order_id>/order_item/create', methods=['POST'])
def order_item_create(order_id):
	menu_item_id = request.json.get('menu_item_id')
	try:
		order_item = OrderList(menu_item_id, order_id)
		db.session.add(order_item)
		db.session.commit()
	except ValueError as error:
		raise UException(message=error.message)
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500)
	return jsonify(status='created', order_item_id=order_item.id), 201

@main.route('/restaurant/orders/<int:order_id>/order_item/<int:order_item_id>/delete', methods=['DELETE'])
def order_item_delete(order_id, order_item_id):
	order_item = OrderList.query.filter_by(id=order_item_id).first()
	if not order_item or order_item.order_id != order_id:
		raise UException('Incorrect order_id or order_item_id')
	try:
		db.session.delete(order_item)
		db.session.commit()
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500)
	return jsonify(status='deleted')

@main.route('/restaurant/<int:restaurant_id>/address/create', methods=['POST'])
def address_create(restaurant_id):
	city = request.json.get('city')
	station = request.json.get('station')
	street = request.json.get('street')
	telephone = request.json.get('telephone')
	try:
		address = Address(restaurant_id, city, street, telephone, station)
		db.session.add(address)
		db.session.commit()
	except ValueError as error:
		raise UException(message=error.message)
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500)
	return jsonify(status='created', address_id=address.id), 201


@main.route('/restaurant/<int:restaurant_id>/address/<int:address_id>/update', methods=['PUT'])
def address_update(restaurant_id, address_id):
	address = Address.query.filter_by(id=address_id).first()
	if not address or address.restaurant_id != restaurant_id:
		raise UException('Incorrect restaurant_id or address_id')
	city = request.json.get('city')
	station = request.json.get('station')
	street = request.json.get('street')
	telephone = request.json.get('telephone')
	try:
		if city: address.city = city
		if station or station=='': address.station = station
		if street: address.street = street
		if telephone: address.telephone = telephone
		db.session.commit()
	except ValueError as error:
		raise UException(message=error.message)
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500)
	return jsonify(status='updated')

@main.route('/restaurant/<int:restaurant_id>/address/<int:address_id>/delete', methods=['DELETE'])
def address_delete(restaurant_id, address_id):
	address = Address.query.filter_by(id=address_id).first()
	if not address or address.restaurant_id != restaurant_id:
		raise UException('Incorrect restaurant_id or address_id')
	try:
		db.session.delete(address)
		db.session.commit()
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500)
	return jsonify(status='deleted')


@main.route('/restaurant/cities/list')
def restaurant_cities():
	cities = []
	try:
		cities = City.get_cities()
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500, payload=exc.message)
	return jsonify(cities)

@main.route('/restaurant/cuisines/list')
def restaurant_cuisines_list():
	cuisines = []
	try:
		cuisines = Cuisine.get_cuisines()
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500, payload=exc.message)
	return jsonify(cuisines)






