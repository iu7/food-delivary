from datetime import datetime
from flask import render_template, session, redirect, url_for, request, make_response
from . import main
import requests
from flask import current_app, abort
from forms import ClientRegisterForm, RestaurantRegisterForm, RestaurantEditForm,AttributesForm,OrderAttributes,\
		AddressForm, ClientEditForm, UserPasswordEditForm, OfficialForm, MenuItemForm, OrderCity
import furls

#TODO ADMIN
@main.route('/about', methods=['GET'])
def about():
	response = render_template('about.html')
	session_id = request.cookies.get('session_id')
	if session_id:
		flag, result = furls.auth_session_state(session_id)
		if flag:
			session_id = result['session_id']
			if result['role'] == 'Client':
				flag, result = furls.client_info(result['user_id'])
				if flag:
					response = make_response(render_template('about.html', user=result))
			elif result['role'] == 'Manager':
				flag, result = furls.restaurant_info(result['user_id'])
				if flag:
					response = make_response(render_template('about.html', user=result))
			response.set_cookie('session_id', session_id)
	return response

#TODO ADMIN
@main.route('/', methods=['GET'])
def index():
	response = render_template('home.html')
	session_id = request.cookies.get('session_id')
	if session_id:
		flag, result = furls.auth_session_state(session_id)
		if flag:
			session_id = result['session_id']
			if result['role'] == 'Client':
				flag, result = furls.client_info(result['user_id'])
				if flag:
					response = make_response(render_template('home.html', user=result))
			elif result['role'] == 'Manager':
				flag, result = furls.restaurant_info(result['user_id'])
				if flag:
					response = make_response(render_template('home.html', user=result))
			else: response = 'Administrator'''
			response.set_cookie('session_id', session_id)
	return response

@main.route('/register', methods=['GET'])
def register():
	response = render_template('register.html')
	return response


@main.route('/client/register', methods=['GET', 'POST'])
def client_register():
	form = ClientRegisterForm()
	if form.validate_on_submit():
		flag, result = furls.client_register(data=form.data)
		if flag:
			response = render_template('home.html')
		else:
			error_message = result['message']
			response = render_template('client_register.html', error_message=error_message, form=form)
			#response = render_template('500.html')
	else: response = render_template('client_register.html', form=form)
	return response


#TODO RESTR
@main.route('/login', methods=['POST'])
def login():
	email = request.form.get('email')
	password = request.form.get('password')
	if email is None or password is None or email == '' or password == '':
		return make_response(render_template('home.html', signin_failure=True))
	if email is not None and password is not None and email != '' and password != '':
		flag, result = furls.auth_login(email=email, password=password)
		if flag:
			session_id = result['session_id']
			if result['role'] == 'Client':
				flag, result = furls.client_info(result['user_id'])
				response = redirect(url_for('main.user_profile', name=result['name']))
			elif result['role'] == 'Manager':
				flag, result = furls.restaurant_info(result['user_id'])
				response = redirect(url_for('main.user_profile', name=result['name']))
			else: 
				response = 'the last is Administartor'
			response.set_cookie('session_id', session_id)
		else:
			response = make_response(render_template('home.html', signin_failure=True))
	else:
		response = render_template('home.html')
	return response


@main.route('/logout')
def logout():
	session_id = request.cookies.get('session_id')
	if not session_id:
		code = 500
	else:
		flag, result = furls.auth_logout(session_id)
		code = 200
	response = make_response(render_template('home.html'))
	return response, code


@main.route('/user/<name>/profile')
def user_profile(name):
	response = render_template('404.html')
	session_id = request.cookies.get('session_id')
	if session_id:
		print 'ONE'
		flag, result = furls.auth_session_state(session_id)
		print result
		if flag:
			if result['role'] == 'Client':
				flag, data = furls.client_info(result['user_id'])
				if flag:
					response = make_response(render_template('client_profile.html', user=data))
			if result['role'] == 'Manager':
				flag, data = furls.restaurant_info(result['user_id'])
				if flag:
					response = make_response(render_template('restaurant_profile.html', user=data))

			response.set_cookie(result['session_id'])	
	return response


@main.route('/user/<name>/profile/data/edit', methods=['GET','POST'])
def user_data_edit(name):
	response = render_template('404.html')
	session_id = request.cookies.get('session_id')
	result_message = request.args.get('result_message')
	error_message = request.args.get('error_message')
	if session_id:
		flag, result = furls.auth_session_state(session_id)
		if flag:
			if result['role'] == 'Client': form = ClientEditForm()
			elif result['role'] == 'Manager': form = RestaurantEditForm()
			if form.validate_on_submit():
				user_id = result['user_id']
				email = request.form.get('email')
				new_name = request.form.get('name')
				telephone = request.form.get('telephone')
				order_email = request.form.get('order_email')
				if result['role'] == 'Client':
					flag, cresult = furls.client_data_update(user_id, email, new_name, telephone)
				elif result['role'] == 'Manager':
					flag, cresult = furls.restaurant_data_update(user_id, email, new_name, telephone, order_email)
				if flag:
					response = redirect(url_for('main.user_data_edit', name=new_name, result_message='Updated!'))
				else:
					response = redirect(url_for('main.user_data_edit', name=name, error_message=cresult['message']))
			else:
				if result['role'] == 'Client':
					flag, uresult = furls.client_info(result['user_id'])
					response = make_response(render_template('client_data_edit.html', \
						user=uresult, form=form, result_message=result_message, error_message=error_message))
				elif result['role'] == 'Manager':
					flag, uresult = furls.restaurant_info(result['user_id'])
					response = make_response(render_template('restaurant_data_edit.html', \
						user=uresult, form=form, result_message=result_message, error_message=error_message))
				response.set_cookie(result['session_id'])
	return response

@main.route('/user/<name>/profile/password/change', methods=['POST', 'GET'])
def user_password_change(name):
	response = render_template('404.html')
	session_id = request.cookies.get('session_id')
	result_message = request.args.get('result_message')
	error_message = request.args.get('error_message')
	if session_id:
		flag, result = furls.auth_session_state(session_id)
		if flag:
			form = UserPasswordEditForm()
			if form.validate_on_submit():
				user_id = result['user_id']
				password = request.form.get('password')
				new_password = request.form.get('new_password')
				flag, cresult = furls.auth_upassw_update(user_id, password, new_password)
				if flag:
					response = redirect(url_for('main.user_password_change', name=name, \
						result_message='Changed!'))
				else:
					response = redirect(url_for('main.user_password_change', name=name, \
						error_message=cresult['message']))
			else:
				if result['role'] == 'Client':
					flag, uresult = furls.client_info(result['user_id'])
					response = make_response(render_template('user_passw_edit.html', user=uresult,\
						form=form, result_message=result_message, error_message=error_message))
				elif result['role'] == 'Manager':
					flag, mresult = furls.restaurant_info(result['user_id'])
					response = make_response(render_template('user_passw_edit.html', user=mresult,\
						form=form, result_message=result_message, error_message=error_message))
				response.set_cookie(result['session_id'])
	return response


@main.route('/client/<name>/address/list')
def client_address_list(name):
	response = render_template('404.html')
	session_id = request.cookies.get('session_id')
	result_message = request.args.get('result_message')
	error_message = request.args.get('error_message')
	if session_id:
		flag, result = furls.auth_session_state(session_id)
		if flag:
			if result['role'] == 'Client':
				flag, cresult = furls.client_address_list(result['user_id'])
				if flag:
					flag, uresult = furls.client_info(result['user_id'])
					address_list=cresult['address_list']
					can_add = (len(address_list) < 5)
					response = make_response(render_template('addresses.html', \
						user=uresult, address_list=address_list, can_add=can_add,\
						error_message=error_message, result_message=result_message))
					response.set_cookie('session_id', result['session_id'])	
	return response



@main.route('/client/<name>/address/create', methods=['GET', 'POST'])
def client_address_create(name):
	response = render_template('404.html')
	session_id = request.cookies.get('session_id')
	result_message = request.args.get('result_message')
	error_message = request.args.get('error_message')
	if session_id:
		flag, result = furls.auth_session_state(session_id)
		if flag and result['role'] == 'Client':
			flag, uresult = furls.client_info(result['user_id'])
			form = AddressForm()
			flag, restr_result = furls.restaurant_get_cities()
			addresses = [(addr, addr) for addr in restr_result['cities_list']]
			form.city.choices = addresses
			if form.validate_on_submit():
				user_id = result['user_id']
				city = request.form.get('city')
				street = request.form.get('street')
				station = request.form.get('station')
				entrance = request.form.get('entrance')
				floor = request.form.get('floor')
				passcode = request.form.get('passcode')
				flag, aresult = furls.client_address_create(user_id, city, street, station, entrance, passcode, floor)
				if flag:				
					response = redirect(url_for('main.client_address_list', name=name, \
							result_message='Address created!'))
				else:
					response = redirect(url_for('main.client_address_list', name=name, \
							error_message=aresult['message']))
			else:	
				response = make_response(render_template('address_create.html',\
					form=form, user=uresult,name=name))
			response.set_cookie('session_id', result['session_id'])
	return response

@main.route('/client/<name>/address/<int:address_id>/delete')
def client_address_delete(name, address_id):
	response = render_template('404.html')
	session_id = request.cookies.get('session_id')
	result_message = request.args.get('result_message')
	error_message = request.args.get('error_message')
	if session_id:
		flag, result = furls.auth_session_state(session_id)
		if flag and result['role'] == 'Client':
			flag, aresult = furls.client_address_delete(address_id)
			if flag:
				response = redirect(url_for('main.client_address_list',
					name=name, result_message='Address deleted!'))
			else:
				response = redirect(url_for('main.client_address_list', \
					name=name, error_message=aresult['message']))
			response.set_cookie('session_id', result['session_id'])
	return response


@main.route('/client/<name>/address/<int:address_id>/update', methods=['POST', 'GET'])
def client_address_update(name, address_id):
	response = render_template('404.html')
	session_id = request.cookies.get('session_id')
	result_message = request.args.get('result_message')
	error_message = request.args.get('error_message')
	if session_id:
		flag, result = furls.auth_session_state(session_id)
		if flag and result['role'] == 'Client':
			flag, uresult = furls.client_info(result['user_id'])
			form = AddressForm()
			city = request.args.get('city')
			flag, restr_result = furls.restaurant_get_cities()
			form.city.choices = [(addr, addr) for addr in restr_result['cities_list'] if addr != city]
			form.city.choices.insert(0, (city, city))
			if form.validate_on_submit():
				city = request.form.get('city')
				street = request.form.get('street')
				station = request.form.get('station')
				entrance = request.form.get('entrance')
				floor = request.form.get('floor')
				passcode = request.form.get('passcode')	
				flag, restr_result = furls.client_address_update(address_id, city,\
					street, station, entrance, passcode, floor)
				if flag:
					response = redirect(url_for('main.client_address_list',\
						name=name, address_id=address_id,result_message='Updated!'))
				else:
					response = redirect(url_for('main.client_address_list',\
						name=name, address_id=address_id,error_message=restr_result['message']))
			else:
				city = request.args.get('city')
				street = request.args.get('street')
				station = request.args.get('station')
				entrance = request.args.get('entrance')
				floor = request.args.get('floor')
				passcode = request.args.get('passcode')
				response = make_response(render_template('addresses_edit.html', \
					user=uresult, form=form, city=city, street=street, station=station,\
					entrance=entrance, passcode=passcode, floor=floor, address_id=address_id))
			response.set_cookie('session_id', result['session_id'])	
	return response

@main.route('/restaurant/register', methods=['GET', 'POST'])
def restaurant_register():
	response = render_template('500.html')
	form = RestaurantRegisterForm()
	form.city.choices = session.get('cities_list')
	form.cuisines.choices = session.get('cuisine_list')
	if form.validate_on_submit():
		flag, result = furls.restaurant_register(form.data)
		if flag:
			response = redirect(url_for('main.index'))
			session.pop('cities_list', None)
			session.pop('cuisine_list', None)
		else:
			response = render_template('restaurant_register.html', form=form, error_message=result['message'])
	else:
		flag, cuisines_result = furls.restaurant_get_cuisines()
		if flag: flag, cities_result = furls.restaurant_get_cities()
		if flag:
			form.city.choices = [(x, x) for x in cities_result['cities_list']]
			session['cities_list'] = form.city.choices
			form.cuisines.choices = [(int(x['id']), x['title']) for x in cuisines_result['cuisine_list']]
			session['cuisine_list'] = form.cuisines.choices
			response = render_template('restaurant_register.html', form=form)
	return response

@main.route('/restaurant/<name>/address', methods=['POST','GET'])
def restaurant_address(name):
	response = make_response(render_template('404.html'))
	session_id = request.cookies.get('session_id')
	result_message = request.args.get('result_message')
	error_message = request.args.get('error_message')
	if session_id:
		flag, result = furls.auth_session_state(session_id)
		if flag and result['role'] == 'Manager':
			session_id = result['session_id']
			flag, restr_result = furls.restaurant_info(result['user_id'])
			flag, address = furls.restaurant_address_list(restr_result['restaurant_id'])	
			form = AddressForm()
			form.city.choices = session.get('cities_list')
			if form.validate_on_submit():
				session.pop('cities_list', None)
				flag, result = furls.restaurant_address_update(address['restaurant_id'], address['id'], form.data)
				if flag:				
					response = redirect(url_for('main.restaurant_address',name=name,result_message='Updated!'))
				else:
					response = redirect(url_for('main.restaurant_address',name=name,error_message=result['message']))
			else:
				flag, cities_result = furls.restaurant_get_cities()
				ch = [(x, x) for x in cities_result['cities_list']  if x != address['city']]
				ch.insert(0, (address['city'],address['city']))
				form.city.choices = ch
				form.station.default = address['station']
				form.process()
				session['cities_list'] = form.city.choices
				response = make_response(render_template('restaurant_addresses.html', result_message=result_message,\
							address=address, form=form, user=restr_result,error_message=error_message))
			response.set_cookie('session_id', session_id)
	return response

@main.route('/restaurant/<name>/officials', methods=['POST', 'GET'])
def restaurant_officials(name):
	response = make_response(render_template('404.html'))
	session_id = request.cookies.get('session_id')
	result_message = request.args.get('result_message')
	error_message = request.args.get('error_message')
	if session_id:
		flag, result = furls.auth_session_state(session_id)
		if flag and result['role'] == 'Manager':
			session_id = result['session_id']
			flag, restr_result = furls.restaurant_info(result['user_id'])
			flag, o_result = furls.restaurant_officials_list(restr_result['restaurant_id'])
			form = OfficialForm(info=o_result['info'])
			if form.validate_on_submit():
				flag, result = furls.restaurant_officials_update(o_result['id'], form.data)
				if flag:
					response = redirect(url_for('main.restaurant_officials', \
						form=form, name=name,result_message='Updated!'))
				else:
					response = redirect(url_for('main.restaurant_officials', \
						form=form,name=name,error_message=result['message']))
			else:
				response = make_response(render_template('official_edit.html', \
						name=restr_result['name'], official=o_result, form=form,user=restr_result,\
						error_message=error_message, result_message=result_message))
			response.set_cookie('session_id', session_id)
	return response

@main.route('/restaurant/<name>/attributes', methods=['POST', 'GET'])
def restaurant_attributes(name):
	response = make_response(render_template('404.html'))
	session_id = request.cookies.get('session_id')
	result_message = request.args.get('result_message')
	error_message = request.args.get('error_message')
	if session_id:
		flag, result = furls.auth_session_state(session_id)
		if flag and result['role'] == 'Manager':
			session_id = result['session_id']
			form = AttributesForm()
			form.cuisines.choices = session.get('cuisine_list')
			form.cuisines_current.choices = session.get('current_cuisine_list')
			if form.validate_on_submit():
				session.pop('cuisine_list', None)
				session.pop('current_cuisine_list', None)
				restaurant_id = session.get('ids')['restaurant_id']
				attribute_id = session.get('ids')['attribute_id']
				flag,result = furls.restaurant_attributes_update(restaurant_id, attribute_id, form.data)
				if flag:
					response = redirect(url_for('main.restaurant_attributes', name=name, result_message='Updated'))
				else:
					response = redirect(url_for('main.restaurant_attributes', name=name, \
								error_message=result['message']))
				session.pop('ids',None)
			else:
				flag, restr_result = furls.restaurant_info(result['user_id'])
				flag, attributes = furls.restaurant_attributes(restr_result['restaurant_id'])
				wdays = attributes['wdays']
				form.delivery_time.default = int(attributes['delivery_time'])
				form.openfrom_h.default = int(attributes['open_from'][:2])
				form.openfrom_m.default = int(attributes['open_from'][3:])
				form.opento_h.default = int(attributes['open_to'][:2])
				form.opento_m.default = int(attributes['open_to'][3:])
				form.online_payment.default = attributes['online_payment']
				form.monday.default = wdays[0]
				form.tuesday.default = wdays[1]
				form.wednesday.default = wdays[2]
				form.thursday.default = wdays[3]
				form.friday.default = wdays[4]
				form.saturday.default = wdays[5]
				form.sunday.default = wdays[6]
				form.process()
				flag, cuisines_result = furls.restaurant_get_cuisines()
				form.cuisines.choices = [(int(x['id']), x['title']) for x in cuisines_result['cuisine_list']\
					if not {'id':x['id'], 'title':x['title']} in attributes['cuisines']]
				form.cuisines_current.choices = [(int(x['id']), x['title']) for x in attributes['cuisines']]
				session['cuisine_list'] = form.cuisines.choices
				session['current_cuisine_list'] = form.cuisines_current.choices
				session['ids'] = {'attribute_id':attributes['attribute_id'], 'restaurant_id':attributes['restaurant_id']}
				response = make_response(render_template('attributes_edit.html', user=restr_result,\
					form=form, error_message=error_message, result_message=result_message,attributes=attributes))
			response.set_cookie('session_id', session_id)
	return response


@main.route('/restaurant/<name>/menu', methods=['GET','POST'])
def restaurant_menu(name):
	response = make_response(render_template('404.html'))
	session_id = request.cookies.get('session_id')
	result_message = request.args.get('result_message')
	error_message = request.args.get('error_message')
	if session_id:
		flag, result = furls.auth_session_state(session_id)
		if flag and result['role'] == 'Manager':
			session_id = result['session_id']
			if flag:
				form = MenuItemForm()
				if form.validate_on_submit():
					menu_id = request.args.get('menu_id')
					restaurant_id = request.args.get('restaurant_id')
					flag, result = furls.restaurant_menu_item_create(restaurant_id, menu_id, form.data)
					if flag:
						response = redirect(url_for('main.restaurant_menu', name=name, result_message='Created!'))
					else:
						response = redirect(url_for('main.restaurant_menu', name=name,\
							error_message=result['message']))
				else:
					flag, restr_result = furls.restaurant_info(result['user_id'])
					flag, menu = furls.restaurant_menu(result['user_id'])
					if form.errors:	error_message = 'Incorrect values'			
					response = make_response(render_template('restaurant_menu.html',\
						user=restr_result, menu_data=menu,form=form,\
						error_message=error_message,result_message=result_message))
			response.set_cookie('session_id', session_id)
	return response

@main.route('/restaurant/<name>/menu/delete')
def restaurant_menu_delete(name):
	response = make_response(render_template('404.html'))
	session_id = request.cookies.get('session_id')
	result_message = request.args.get('result_message')
	error_message = request.args.get('error_message')
	if session_id:
		flag, result = furls.auth_session_state(session_id)
		if flag and result['role'] == 'Manager':
			session_id = result['session_id']
			restaurant_id = request.args.get('restaurant_id')
			menu_id = request.args.get('menu_id')
			menu_item_id = request.args.get('menu_item_id')
			if menu_item_id and restaurant_id and menu_id:
				flag, result = furls.restaurant_menu_delete(restaurant_id, menu_id, menu_item_id)
				if flag:
					response = redirect(url_for('main.restaurant_menu',name=name,result_message='Updated!'))
				else:
					response = redirect(url_for('main.restaurant_menu',name=name,error_message=result['message']))	
			response.set_cookie('session_id', session_id)
	return response

@main.route('/restaurant/<name>/menu/update', methods=['GET', 'POST'])
def restaurant_menu_update(name):
	response = make_response(render_template('404.html'))
	session_id = request.cookies.get('session_id')
	result_message = request.args.get('result_message')
	error_message = request.args.get('error_message')
	menu_id = request.args.get('menu_id')
	restaurant_id = request.args.get('restaurant_id')
	menu_item_id = request.args.get('menu_item_id')
	if session_id:
		flag, result = furls.auth_session_state(session_id)
		if flag and result['role'] == 'Manager':
			form = MenuItemForm()
			if form.validate_on_submit():
				flag, result = furls.restaurant_menu_update(restaurant_id, menu_id, menu_item_id, form.data)
				if flag:
					response = redirect(url_for('main.restaurant_menu', name=name, result_message='Updated'))
				else:
					response = redirect(url_for('main.restaurant_menu_edit', name=name, \
					error_message=result['message'],menu_id=menu_id,\
					restaurant_id=restaurant_id,menu_item_id=menu_item_id))
			else:
				flag, restr_result = furls.restaurant_info(result['user_id'])
				form.title.default = request.args.get('title')
				form.price.default = request.args.get('price')
				form.info.default = request.args.get('info')
				form.process()
				response = make_response(render_template('restaurant_menu_edit.html',user=restr_result, form=form,\
				error_message=error_message,result_message=result_message,menu_id=menu_id,\
				restaurant_id=restaurant_id,menu_item_id=menu_item_id))
			response.set_cookie('session_id', session_id)
	return response


#ORDERS AND MENUS
@main.route('/orders/make_order', methods=['POST', 'GET'])
def make_order():
	response = make_response(render_template('404.html'))
	session_id = request.cookies.get('session_id')
	user = None
	if session_id:
		flag, result = furls.auth_session_state(session_id, user_data=True)	
		if flag: user = result['user']

	form = OrderCity()
	form.cities.choices = session.get('cities')
	if request.method == 'POST' and form.cities.choices is None:
		flag, result = furls.restaurant_get_cities(real_city=True)
		form.cities.choices = [(x,x) for x in result['cities_list']]
	if form.validate_on_submit():
		session.pop('cities', None)
		response = redirect(url_for('main.make_order_menus', city=form.data.get('cities')))
	else:
		flag, result = furls.restaurant_get_cities(real_city=True)
		form.cities.choices = [(x,x) for x in result['cities_list']]
		session['cities'] = form.cities.choices
		response = make_response(render_template('orders_city.html', user=user, form=form))
	if session_id: response.set_cookie('session_id', session_id)
	return response


@main.route('/orders/make_order/<city>/restaurants', methods=['POST', 'GET'])
def make_order_menus(city):
	response = make_response(render_template('404.html'))
	session_id = request.cookies.get('session_id')
	user = None
	if session_id:
		flag, result = furls.auth_session_state(session_id, user_data=True)	
		if flag: user = result['user']
	form = OrderAttributes()
	if form.validate_on_submit():
		cuisine_check_list = request.form.getlist('cuisine_list')
		flag, result = furls.restaurants_by_preferences(form.data, cuisine_check_list, city)
		response = make_response(render_template('orders_page.html',form=form,user=user,\
					city=city, cuisines=result['cuisine_list'], restaurants=result['restaurant_list']))
	else:
		flag, result = furls.restaurant_get_cuisines(city)
		response = make_response(render_template('orders_page.html',form=form,user=user,\
					city=city,cuisines=result['cuisine_list'],first=True))
	if session_id: response.set_cookie('session_id', session_id)
	return response

@main.route('/orders/make_order/<city>/restaurants/<name>/menu', methods=['POST', 'GET'])
def make_order_from_restaurant(city, name):
	return 'Hey !'



