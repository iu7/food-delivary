from ConfigParser import SafeConfigParser
settings = SafeConfigParser()
settings.read('/home/bakit/CP/front/settings.cfg')

logic_url = settings.get('LogicBackend', 'URL') + settings.get('LogicBackend', 'PORT')
import requests
import json

JSON_HEADER = {'Content-Type' : 'application/json'}

def client_register(data):
	api_url = logic_url + '/client/register'
	r = requests.post(api_url, data=json.dumps(data), headers=JSON_HEADER)
	if r.status_code == 201:
		flag = True
	else: flag = False
	return flag, json.loads(r.text)

def client_info(user_id):
	api_url = logic_url + '/client/info'
	r = requests.get(api_url, params={'user_id':user_id})
	if r.status_code == 200: flag = True
	else: flag = False
	return flag, json.loads(r.text)

def client_data_update(user_id, email, name, telephone):
	api_url = logic_url + '/client/data/update'
	r = requests.put(api_url, \
		data=json.dumps({'user_id':user_id, 'email':email, 'name':name, 'telephone':telephone}),headers=JSON_HEADER)
	if r.status_code == 200: flag = True
	else: flag = False
	return flag, json.loads(r.text)

def client_address_list(user_id):
	api_url = logic_url + '/client/address/list'
	r  = requests.get(api_url, params={'user_id':user_id})
	if r.status_code == 200: flag = True
	else: flag = False
	return flag, json.loads(r.text)

def client_address_create(user_id, city, street, station=None, entrance=None, passcode=None,floor=None):
	api_url = logic_url + '/client/address/create'
	r = requests.post(api_url, \
		data=json.dumps({'user_id':user_id, 'city':city, 'street':street, 'station':station, \
				'entrance':entrance, 'passcode':passcode, 'floor':floor}), headers=JSON_HEADER)
	if r.status_code == 201: flag = True
	else: flag = False
	return flag, json.loads(r.text)

def client_address_delete(address_id):
	api_url = logic_url + '/client/address/delete'
	r = requests.delete(api_url, data=json.dumps({'address_id':address_id}), headers=JSON_HEADER)
	if r.status_code == 200: flag = True
	else: flag = False
	return flag, json.loads(r.text)

def client_address_update(address_id, city, street, station=None, entrance=None, passcode=None,floor=None):
	api_url = logic_url + '/client/address/update'
	r = requests.put(api_url, \
		data=json.dumps({'address_id':address_id, 'city':city, 'street':street, 'station':station, \
				'entrance':entrance, 'passcode':passcode, 'floor':floor}), headers=JSON_HEADER)
	if r.status_code == 200: flag = True
	else: flag = False
	return flag, json.loads(r.text)




def auth_upassw_update(user_id, password, new_password):
	api_url = logic_url + '/auth/user/password/update'
	r = requests.put(api_url, \
		data=json.dumps({'user_id':user_id,'password':password, 'new_password':new_password}), headers=JSON_HEADER)
	if r.status_code == 200: flag = True
	else: flag = False
	return flag, json.loads(r.text)

def auth_login(email, password):
	api_url = logic_url + '/auth/login'
	r = requests.get(api_url, params={'email':email, 'password':password})
	if r.status_code == 200:
		flag = True
	else: flag = False
	return flag, json.loads(r.text)

def auth_session_state(session_id, user_data=False):
	api_url = logic_url + '/auth/session/state'
	r = requests.get(api_url, data=json.dumps({'session_id':session_id, 'user_data' : user_data}), headers=JSON_HEADER)
	data = json.loads(r.text)
	if r.status_code == 200: 
		flag = True
		if data['expired']:
			flag = False
		else: flag = True
	else: 
		flag = None
	return flag, data


def auth_logout(session_id):
	api_url = logic_url + '/auth/logout'
	r = requests.get(api_url, params={'session_id':session_id})
	if r.status_code == 200: flag = True
	else: flag = False
	return flag, json.loads(r.text)

######################################################
######################################################
def restaurant_get_cities(real_city=False):
	api_url = logic_url + '/restaurant/cities/list'
	r = requests.get(api_url, data=json.dumps({'real_city':real_city}), headers=JSON_HEADER)
	if r.status_code == 200: flag = True
	else: flag = False
	return flag, json.loads(r.text)


def restaurant_get_cuisines(city=None):
	api_url = logic_url + '/restaurant/cuisines/list'
	if city is not None:
		r = requests.get(api_url, params={'city':city})
	else:
		r = requests.get(api_url)
	if r.status_code == 200: flag = True
	else: flag = False
	return flag, json.loads(r.text)

def restaurant_register(data):
	api_url = logic_url + '/restaurant/register'
	r = requests.post(api_url, data=json.dumps(data), headers=JSON_HEADER)
	if r.status_code == 201:
		flag = True
	else: flag = False
	return flag, json.loads(r.text)

def restaurant_info(user_id):
	api_url = logic_url + '/restaurant/info'
	r = requests.get(api_url, data=json.dumps({'user_id':user_id}),headers=JSON_HEADER)
	if r.status_code == 200:
		flag = True
	else: flag = False
	return flag, json.loads(r.text)

def restaurant_data_update(user_id, email, name, telephone, order_email):
	api_url = logic_url + '/restaurant/data/update'
	r = requests.put(api_url, \
		data=json.dumps({'user_id':user_id, 'email':email, \
			'order_email':order_email, 'name':name, 'telephone':telephone}),headers=JSON_HEADER)
	if r.status_code == 200: flag = True
	else: flag = False
	return flag, json.loads(r.text)

def restaurant_address_list(restaurant_id):
	api_url = logic_url + '/restaurant/address/list'
	r = requests.get(api_url, data=json.dumps({'restaurant_id':restaurant_id}), headers=JSON_HEADER)
	if r.status_code == 200:
		flag = True
		address = json.loads(r.text)
		if len(address) > 0: address = address['restaurant_address_list'][0]['address']
		else: flag = False
	else: flag = False
	return flag, address

def restaurant_address_update(restaurant_id, address_id, data):
	api_url = logic_url + '/restaurant/address/update'
	r = requests.put(api_url, data=json.dumps({'data':data, \
			'restaurant_id':restaurant_id, 'address_id':address_id}), headers=JSON_HEADER)
	if r.status_code == 200:
		flag = True
	else: flag = False
	return flag, json.loads(r.text)

def restaurant_officials_list(restaurant_id):
	api_url = logic_url + '/restaurant/officials/list'
	r = requests.get(api_url, data=json.dumps({'restaurant_id':restaurant_id}), headers=JSON_HEADER)
	if r.status_code == 200:
		flag = True
		official = json.loads(r.text)['officials_list']
		if len(official) > 0: official = official[0]['officials']
	else: flag = False
	return flag, official

def restaurant_officials_update(officials_id, data):
	api_url = logic_url + '/restaurant/officials/update'
	r = requests.put(api_url, data=json.dumps({'data':data, 'officials_id':officials_id}), headers=JSON_HEADER)
	if r.status_code == 200:
		flag = True
	else: flag = False
	return flag, json.loads(r.text)

def restaurant_attributes(restaurant_id):
	api_url = logic_url + '/restaurant/attributes'
	r = requests.get(api_url, data=json.dumps({'restaurant_id':restaurant_id}), headers=JSON_HEADER)
	if r.status_code == 200:
		flag = True
		attributes = json.loads(r.text)
		result = attributes['attributes']
		result['cuisines'] = attributes['cuisines']
	else: 
		flag = False
		result = json.loads(r.text)
	return flag, result

def restaurant_attributes_update(restaurant_id, attribute_id, data):
	api_url = logic_url + '/restaurant/attributes/update'
	r = requests.put(api_url, data=json.dumps({'attribute_id':attribute_id, 'restaurant_id':restaurant_id, 'data':data}),\
							headers=JSON_HEADER)
	if r.status_code == 200:
		flag = True
	else: flag = False
	return flag, json.loads(r.text)


def restaurant_menu(user_id):
	api_url = logic_url + '/restaurant/menu'
	r = requests.get(api_url, data=json.dumps({'user_id':user_id}), headers=JSON_HEADER)
	if r.status_code == 200:
		flag = True
	else: flag = False
	return flag, json.loads(r.text)

def restaurant_menu_delete(restaurant_id, menu_id, menu_item_id):
	api_url = logic_url + '/restaurant/menu_item/delete'
	r = requests.delete(api_url, data=json.dumps({'restaurant_id':restaurant_id, 'menu_id':menu_id, 'menu_item_id':menu_item_id}),\
							headers=JSON_HEADER)
	if r.status_code == 200:
		flag = True
	else: flag = False
	return flag, json.loads(r.text)


def restaurant_menu_item_create(restaurant_id, menu_id, data):
	api_url = logic_url + '/restaurant/menu_item/create'
	r = requests.post(api_url, data=json.dumps({'data':data,'menu_id':menu_id,'restaurant_id':restaurant_id}), headers=JSON_HEADER)
	if r.status_code == 201:
		flag = True
	else: flag = False
	return flag, json.loads(r.text)

def restaurant_menu_update(restaurant_id, menu_id, menu_item_id, data):
	api_url = logic_url + '/restaurant/menu_item/update'
	r = requests.put(api_url, data=json.dumps({'data':data,'menu_id':menu_id,'restaurant_id':restaurant_id,\
					'menu_item_id':menu_item_id}), headers=JSON_HEADER)
	if r.status_code == 200:
		flag = True
	else: flag = False
	return flag, json.loads(r.text)

def restaurant_cities_add(city):
	api_url = logic_url + '/restaurant/cities/add'
	r = requests.post(api_url, data=json.dumps({'city':city}), headers=JSON_HEADER)
	if r.status_code == 201:
		flag = True
	else: flag = False
	return flag, json.loads(r.text)

	






