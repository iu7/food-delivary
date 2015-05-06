from datetime import datetime
from . import main
from flask import request, jsonify, session
from .. import db
from .. exceptions import UException
import requests
from flask import current_app
import furls

JSONH = {'Content-Type' : 'application/json'}

@main.route('/')
def index():
	return 'logic service'


@main.route('/client/register', methods=['POST'])
def client_register():
	code = 201
	email = request.json.get('email')
	password = request.json.get('password')
	name = request.json.get('name')
	telephone = request.json.get('telephone')
	flag, auth_data = furls.auth_register(email, password)
	if flag:
		user_id = auth_data['user_id']
		try:
			flag, cli_data = furls.cli_register(user_id, name, telephone)
			if flag:
				result = cli_data
			else: raise Exception()
		except:
			flag, auth_data = furls.auth_user_raw_delete(user_id)
			if not flag:
				raise UException(message='Unexpected server error', status_code=500, payload=auth_data['message'])
			else:
				raise UException(message=cli_data['message'])
	else:
		raise UException(message=auth_data['message'])
	return jsonify(data=result), code
	
@main.route('/auth/login')
def auth_login():
	email = request.args.get('email')
	password = request.args.get('password')
	flag, result = furls.auth_login(email, password)
	if flag:
		code = 200
	else:
		code = auth_result['status_code']
	return jsonify(result), code

@main.route('/auth/session/state')
def auth_session_state():
	session_id = request.json.get('session_id')
	user_data = request.json.get('user_data')
	if not session_id:
		raise UException('Incorrect request')
	flag, auth_result = furls.auth_session_state(session_id)
	if flag:
		if not auth_result['expired']:
			result = auth_result
			code = 200
			if user_data:
				if result['role'] == 'Client':	
					flag, user_result = furls.cli_info(result['user_id'])
				elif result['role'] == 'Manager':
					flag, user_result = furls.restaurant_info(result['user_id'])
				elif result['role'] == 'Administrator':
					user_result = {'name' : 'Administrator'}
				if flag:
					#user_result['email'] == result['email']
					result['user'] = user_result
					code = 200
				else:
					code = result['status_code']
		else: 
			result = auth_result
			code = result['status_code']
	else:
		result = auth_result
		code = result['status_code']
	return jsonify(result), code


@main.route('/auth/logout')
def auth_logout():
	session_id = request.args.get('session_id')
	flag, result = furls.auth_logout(session_id)
	if flag: code = 200
	else: code = result['status_code']
	return jsonify(result), code


@main.route('/client/data/update', methods=['PUT'])
def client_data_update():
	user_id = request.json.get('user_id')
	email = request.json.get('email')
	telephone = request.json.get('telephone')
	name = request.json.get('name')
	if user_id is None:
		raise UException('Incorrect request')
	flag, auth_result = furls.auth_uemail_update(user_id, email)
	if flag:
		flag, result = furls.cli_update(user_id, name, telephone)
		if flag:
			code = 200
		else:
			code = result['status_code']
	else:
		result = auth_result
		code = result['status_code']
	return jsonify(result), code


@main.route('/auth/user/password/update', methods=['PUT'])
def auth_user_password_update():
	user_id = request.json.get('user_id')
	password = request.json.get('password')
	new_password = request.json.get('new_password')
	if not user_id or not password or not new_password:
		raise UException('Incorrect request')
	flag, result = furls.auth_upassw_update(user_id, password, new_password)
	if flag:
		code = 200
	else: code = result['status_code']
	return jsonify(result), code


@main.route('/client/address/list')
def client_address_list():
	user_id = request.args.get('user_id')
	if not user_id:
		raise UException('Incorrect request: user_id is required')
	flag, result = furls.cli_address_list(user_id)
	if flag:
		code = 200
	else: code = result['status_code']
	return jsonify(result), code

@main.route('/restaurant/cities/list')
def restaurant_cities():
	cities = None
	real_city = request.json.get('real_city')
	try:
		flag, result = furls.restr_get_cities(real_city=real_city)
		if flag: code = 200
		else: code = result['status_code']
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500, payload=exc.message)
	return jsonify(cities_list=result['cities_list'])

@main.route('/restaurant/cuisines/list')
def restaurant_cuisines():
	cities = []
	city = request.args.get('city')
	try:
		flag, result = furls.restr_get_cuisines(city)
		if flag: code = 200
		else: code = result['status_code']
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500, payload=exc.message)
	return jsonify(cuisine_list=result['cuisine_list'])



@main.route('/client/address/create', methods=['POST'])
def client_address_create():
	user_id = request.json.get('user_id')
	city = request.json.get('city')
	street = request.json.get('street')
	station = request.json.get('station')
	entrance = request.json.get('entrance')
	floor = request.json.get('floor')
	passcode = request.json.get('passcode')
	if user_id is None or city is None or street is None:
		raise UException('Incorrect request')
	try:
		flag, result = furls.cli_address_create(user_id, city, street, station, entrance, passcode, floor)
		if flag: code = 201
		else: code = result['status_code']
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500, payload=exc.message)
	return jsonify(result), code

@main.route('/client/address/delete', methods=['DELETE'])
def client_address_delete():
	address_id = request.json.get('address_id')
	flag, result = furls.cli_address_delete(address_id)
	if flag: code = 200
	else: code = result['message']
	return jsonify(result), code


@main.route('/client/address/update', methods=['PUT'])
def client_address_update():
	address_id = request.json.get('address_id')
	city = request.json.get('city')
	street = request.json.get('street')
	station = request.json.get('station')
	entrance = request.json.get('entrance')
	floor = request.json.get('floor')
	passcode = request.json.get('passcode')
	if address_id is None or city is None or street is None:
		raise UException('Incorrect request')
	try:
		flag, result = furls.cli_address_update(address_id, city, street, station, entrance, passcode, floor)
		if flag: code = 200
		else: code = result['status_code']
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500, payload=exc.message)
	return jsonify(result), code


@main.route('/restaurant/register', methods=['POST'])
def restaurant_register():
	email = request.json.get('email')
	password = request.json.get('password')
	open_from = request.json.get('openfrom_h') + request.json.get('openfrom_m')
	open_to = request.json.get('opento_h') + request.json.get('opento_m')
	min_payment = request.json.get('min_price')
	delivery_payment = request.json.get('delivery_payment')
	delivery_time = request.json.get('delivery_time')
	online_payment = request.json.get('online_payment')
	city = request.json.get('city')
	street = request.json.get('street')
	telephone = request.json.get('telephone')
	order_email = request.json.get('order_email')
	name = request.json.get('name')
	station = request.json.get('station')
	official_name = request.json.get('official_name') 
	official_email = request.json.get('official_email')
	official_telephone = request.json.get('official_telephone')
	info = request.json.get('info')
	cuisines = request.json.get('cuisines')
	wdays = [request.json.get('monday'),request.json.get('tuesday'),request.json.get('wednesday'),request.json.get('thursday'),\
				request.json.get('friday'),request.json.get('saturday'),request.json.get('sunday')]
	restaurant_id = None
	user_id = None
	flag, auth_data = furls.auth_register(email, password, role='Manager')
	if flag:
		user_id = auth_data['user_id']
		try:
			restr_flag, restr_data = furls.restr_register(user_id, name, order_email, telephone)
			if restr_flag:
				restaurant_id = restr_data['restaurant_id']
				attr_flag, attr_data = furls.restr_attributes_create(restaurant_id, open_from, open_to,\
					min_payment, delivery_payment, delivery_time, wdays, online_payment)
				if attr_flag:
					addr_flag, addr_data = furls.restr_address_create(restaurant_id, \
								city, street, telephone, station)
					if addr_flag:
						off_flag, off_result = furls.restr_officials_create(restaurant_id, \
								official_name, official_email, official_telephone, info)
						if off_flag:
							if len(cuisines) > 0:
								cuis_flag, cuis_data = furls.restr_cuisines_add(restaurant_id, cuisines)
								if not cuis_flag:
									err_data = cuis_data
									raise Exception()
							result = restr_data
							code = 201
						else:
							err_data = off_result
							raise Exception()
					else:
						err_data = addr_data
						raise Exception()
				else:
					err_data = attr_data
					raise Exception()
			else:
				err_data = restr_data
				raise Exception()
		except:
			if user_id:
				auth_flag, auth_data = furls.auth_user_raw_delete(user_id)
			if restaurant_id:
				restr_flag, restr_data = furls.restr_delete(restaurant_id)
			code = err_data['status_code']
			message = err_data['message']
			if not auth_flag:
				raise UException(message='Unexpected server error', status_code=500, payload=auth_data['message'])
			if not restr_flag:
				raise UException(message='Unexpected server error', status_code=500, payload=restr_data['message'])
			else:
				raise UException(message=message, status_code=code)
	else:
		raise UException(message=auth_data['message'])
	return jsonify(data=result), code


@main.route('/client/info')
def client_info():
	user_id = request.args.get('user_id')
	flag, result = furls.cli_info(user_id)
	if flag:
		flag, auth_result = furls.auth_user_info(user_id)
		if flag:
			code = 200
			result['email'] = auth_result['email']
		else:
			code = result['status_code']
			result = auth_result
	else:
		code = result['status_code']
	return jsonify(result), code

@main.route('/user/list/<role>')
def user_list(role):
	if not role:
		raise UException('Incorrect request')
	flag, users = furls.auth_users_by_role(role)
	if flag:
		#user_id_list = users['user_id_list']
		if role == 'Client':
			flag, result = furls.client_list()
			for client in result['clients']:
				for user in users['users']:
					if user['user_id'] == client['user_id']:
							client['email'] = user['email']
		elif role == 'Manager':
			flag, result = furls.restaurant_list()
		else:
			raise UException('Incorrect request')
		code=  200
	else:
		result = users = []
		code = result['status_code']
	return jsonify(result=result), code



@main.route('/restaurant/info')
def restaurant_info():
	user_id = request.json.get('user_id')
	restaurant_id = request.json.get('restaurant_id')
	if not user_id and not restaurant_id:
		raise UException('Incorrect request')
	flag, result = furls.restaurant_info(user_id, restaurant_id)
	if flag:
		flag, auth_result = furls.auth_user_info(user_id)
		if flag:
			code = 200
			result['email'] = auth_result['email']
		else:
			code = result['status_code']
			result = auth_result
	else:
		code = result['status_code']
	return jsonify(result), code




@main.route('/restaurant/data/update', methods=['PUT'])
def restaurant_data_update():
	user_id = request.json.get('user_id')
	email = request.json.get('email')
	order_email = request.json.get('order_email')
	telephone = request.json.get('telephone')
	name = request.json.get('name')
	if not user_id:
		raise UException('Incorrect request')
	flag, result = furls.restaurant_info(user_id)
	if flag:
		flag, auth_result = furls.auth_user_info(user_id)
		old_email = auth_result['email']
		flag, auth_result = furls.auth_uemail_update(user_id, email)
		if flag:
			flag, restr_result = furls.restaurant_info(user_id)
			restaurant_id = restr_result['restaurant_id']
			flag, restr_result = furls.restaurant_update(restaurant_id, order_email, telephone, name)
			if flag: code = 200
			else:
				flag, auth_result = furls.auth_uemail_update(user_id, old_email)
				code = restr_result['code']
			result = restr_result
		else:
			code = auth_result['status_code']
			result = auth_result		
	else:
		code = result['status_code']
	return jsonify(result), code



@main.route('/restaurant/address/list')
def restaurant_address_list():
	restaurant_id = request.json.get('restaurant_id')
	if not restaurant_id:
		raise UException('Incorrect request')
	flag, result = furls.restaurant_address_list(restaurant_id)
	if not flag: code = result['status_code']
	else: code = 200
	return jsonify(result), code

@main.route('/restaurant/address/update', methods=['PUT'])
def restaurant_address_update():
	address_id = request.json.get('address_id')
	restaurant_id = request.json.get('restaurant_id')
	data = request.json.get('data')
	if not address_id or not restaurant_id:
		raise UException('Incorrect request')
	flag, result = furls.restaurant_address_update(restaurant_id, address_id, data)
	if not flag: code = result['status_code']
	else: code = 200
	return jsonify(result), code

@main.route('/restaurant/officials/list')
def restaurant_officials_list():
	restaurant_id = request.json.get('restaurant_id')
	if not restaurant_id:
		raise UException('Incorrect request')
	flag, result = furls.restaurant_officials_list(restaurant_id)
	if flag: code = 200
	else: code = result['status_code']
	return jsonify(result), code

@main.route('/restaurant/officials/update', methods=['PUT'])
def restaurant_officials_update():
	officials_id = request.json.get('officials_id')
	data = request.json.get('data')
	if not officials_id or not data:
		raise UException('Incorrect request')	
	flag, result = furls.restaurant_officials_update(officials_id, data)
	if flag: code = 200
	else: code = result['status_code']
	return jsonify(result), code

@main.route('/restaurant/attributes')
def restaurant_attributes():
	restaurant_id = request.json.get('restaurant_id')
	if not restaurant_id:
		raise UException('Incorrect request')
	flag, result = furls.restaurant_attributes(restaurant_id)
	if flag: code = 200
	else: code = result['status_code']
	return jsonify(result), code


@main.route('/restaurant/attributes/update', methods=['PUT'])
def restaurant_attributes_update():
	data = request.json.get('data')
	attribute_id = request.json.get('attribute_id')
	restaurant_id = request.json.get('restaurant_id')
	if not data:
		raise UException('Incorrect request')
	wdays=[data['monday'],data['tuesday'],data['wednesday'],data['thursday'],\
			data['friday'],data['saturday'],data['sunday']]
	open_to = data['opento_h'] + ':' + data['opento_m']
	open_from = data['openfrom_h'] + ':' + data['openfrom_m']
	flag, result = furls.restaurant_attributes_update(attribute_id, open_from, \
			open_to, data['min_price'], data['delivery_payment'], data['delivery_time'], data['online_payment'],wdays)
	if flag:
		code = 200
		if data['cuisines_current']:
			flag, result = furls.restr_cuisines_delete(restaurant_id, data['cuisines_current'])
			if not flag: code = result['status_code']
		if flag and data['cuisines']:
			flag, result = furls.restr_cuisines_add(restaurant_id, data['cuisines'])
			if not flag: code = result['status_code']
	else:
		code = result['status_code']
	return jsonify(result), code


@main.route('/restaurant/menu')
def restaurant_menu():
	user_id = request.json.get('user_id')
	restaurant_id = request.json.get('restaurant_id')
	if not user_id and not restaurant_id:
		raise UException('Incorrect request')
	if not restaurant_id:
		flag, result = furls.restaurant_info(user_id)
	else: flag = True
	if flag:
		if not restaurant_id:
			restaurant_id = result['restaurant_id']
		flag, result = furls.restaurant_menu(restaurant_id)
		if not flag:
			code = result['status_code']
		else: code = 200
	else:
		code = result['status_code']
	return jsonify(result), code

@main.route('/restaurant/menu_item/delete', methods=['DELETE'])
def restaurant_menu_item_delete():
	menu_id = request.json.get('menu_id')
	menu_item_id = request.json.get('menu_item_id')
	restaurant_id = request.json.get('restaurant_id')
	if not menu_id or not menu_item_id or not restaurant_id:
		raise UException('Incorrect request')
	flag, result = furls.restaurant_menu_delete(restaurant_id, menu_id, menu_item_id)
	if not flag: code = result['status_code']
	else: code = 200
	return jsonify(result), code

@main.route('/restaurant/menu_item/create', methods=['POST'])
def restaurant_menu_item_create():
	restaurant_id = request.json.get('restaurant_id')
	menu_id = request.json.get('menu_id')
	data = request.json.get('data')
	if not data or not restaurant_id or not menu_id:
		raise UException('Incorrect request')
	flag, result = furls.restaurant_menu_item_create(restaurant_id, menu_id, data)
	if flag: code = 201
	else: code = result['status_code']
	return jsonify(result), code




@main.route('/restaurant/menu_item/update', methods=['PUT'])
def restaurant_menu_item_update():
	menu_id = request.json.get('menu_id')
	menu_item_id = request.json.get('menu_item_id')
	restaurant_id = request.json.get('restaurant_id')
	data = request.json.get('data')
	if not menu_id or not menu_item_id or not restaurant_id or not data:
		raise UException('Incorrect request')
	flag, result = furls.restaurant_menu_update(restaurant_id, menu_id, menu_item_id, data)
	if not flag: code = result['status_code']
	else: code = 200
	return jsonify(result), code



@main.route('/restaurant/cities/add', methods=['POST'])
def restaurant_cities_add():
	city = request.json.get('city')
	if not city:
		raise UException('Incorrect request')
	flag, result = furls.restaurant_cities_add(city)
	if flag: code = 201
	else: code = result['status_code']
	return jsonify(result), code


@main.route('/restaurant/list/by_preferences')
def restaurants_by_preferences():
	data = request.json.get('data')
	if not data:
		raise UException('Incorrect request')
	flag, result = furls.restaurants_by_preferences(data)
	if not flag: code = result['status_code']
	else: code = 200
	return jsonify(result), code
	

@main.route('/restaurant/order/confirmation', methods=['POST'])
def restaurant_order_confirmation():
	code = 400
	if not request.json:
		raise UException('Incorrect request')
	else:
		restaurant_id = request.json.get('restaurant_id')
		if not restaurant_id: raise UException('Incorrect request')
		flag, result = furls.restaurant_order_confirm(restaurant_id, request.json)
		if flag: code = 201
		else: code = result['status_code']
	return jsonify(result), code


@main.route('/user/profile/delete', methods=['DELETE'])
def user_profile_delete():
	code = 400
	user_id = request.args.get('user_id')
	session_id = request.args.get('session_id')
	if not user_id or not session_id:
		raise UException('Incorrect request')
	flag, auth_result = furls.auth_session_state(session_id)
	if flag:
		if not auth_result['expired']:
			flag, logout_result = furls.auth_logout(session_id)
			flag, user_result = furls.auth_user_raw_delete(user_id)
			client_result = restaurant_result = None
			if auth_result['role'] == 'Client':	
				flag, client_result = furls.cli_delete(auth_result['user_id'])
			elif auth_result['role'] == 'Manager':
				flag,restaurant_result = furls.restr_delete(auth_result['user_id'])
			result = {'logout':logout_result, 'user':user_result, 'client':client_result, 'restaurant':restaurant_result}
			code = 200
		else:
			result = {'session_expired':True}
	else:
		result = auth_result
	return jsonify(result), code
		

@main.route('/restaurant/client/history')
def client_history():
	user_id = request.args.get('user_id')
	if not user_id:
		raise UException('Incorrect request')
	flag, result = furls.restaurant_client_history(user_id)
	if flag: code = 200
	else:
		code = result['status_code']
	return jsonify(result), code


@main.route('/restaurant/history')
def restaurant_history():
	data = request.json.get('data')
	if not data:
		raise UException('Incorrect request')
	flag, result = furls.restaurant_history(data)
	if flag: code = 200
	else: code = result['status_code']
	return jsonify(result), code


@main.route('/restaurant/order/status/change', methods=['PUT'])
def restaurant_order_status_change():
	status_type = request.json.get('status_type')
	order_id = request.json.get('order_id')
	restaurant_id = request.json.get('restaurant_id')
	if not status_type or not order_id or not restaurant_id:
		raise UException('Incorrect request')
	flag, result = furls.restaurant_order_status_change(restaurant_id, order_id, status_type)
	if flag: code = 200
	else: code = result['status_code']
	return jsonify(result), code









