from datetime import datetime
from . import main
from flask import request, jsonify
from .. import db
from .. models import Client, History, Address
from .. exceptions import UException

@main.route('/')
def index():
	return ''

@main.route('/client/register', methods=['POST'])
def client_register():
	name = request.json.get('name')
	user_id = request.json.get('user_id')
	telephone = request.json.get('telephone')
	if name is None or user_id is None or telephone is None:
		raise UException('Incorrect request: incorrect parameters')
	try:
		client = Client(name, telephone, user_id)
		db.session.add(client)
		db.session.commit()
	except ValueError as error:
		raise UException(message=error.message)
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500, payload=exc.message)
	return jsonify(status='created', name=client.name, user_id=user_id), 201

@main.route('/client/data/points/update', methods=['PUT'])
def client_data_points_update():
	user_id = request.json.get('user_id')
	points = request.json.get('points')
	if user_id is None or points is None:
		raise UException('Incorrect request: user_id required')
	client = Client.query.filter_by(user_id=user_id).first()
	if not client:
		raise UException('Incorrect user_id')
	try:
		client.update_points(points)
		db.session.commit()
	except ValueError as error:
		raise UException(message=error.message)
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500, payload=exc.message)
	return jsonify(status='updated', points=client.points, user_id=user_id)

@main.route('/client/data/update', methods=['PUT'])
def client_data_update():
	name = request.json.get('name')
	user_id = request.json.get('user_id')
	telephone = request.json.get('telephone')
	if user_id is None:
		raise UException('Incorrect request: user_id required')
	client = Client.query.filter_by(user_id=user_id).first()
	if not client:
		raise UException('Incorrect user_id')
	try:
		if name is not None: client.name = name
		if telephone is not None: client.telephone = telephone
		db.session.commit()
	except ValueError as error:
		raise UException(message=error.message)
	except Exception as exc:
		raise UException(message='Unexpected server exception', status_code=500, payload=exc.message)
	return jsonify(status='updated')

@main.route('/client/delete', methods=['DELETE'])
def client_delete():
	user_id = request.json.get('user_id')
	if not user_id:
		raise UException('Incorrect query')
	client = Client.query.filter_by(user_id=user_id).first()
	if not client:
		raise UException('Incorrect user_id')
	try:
		db.session.delete(client)
		db.session.commit()
	except:
		raise UException(message='Unexpected server exception', status_code=500)
	return jsonify(status='deleted')

@main.route('/client/info')
def client_info():
	user_id = request.args.get('user_id')
	if not user_id:
		raise UException('Incorrect query')
	client = Client.query.filter_by(user_id=user_id).first()
	if not client:
		raise UException('Incorrect user_id')
	return jsonify(name=client.name, telephone=client.telephone, client_id=client.id, \
		 points=client.points, member_since=client.member_since.strftime('%d.%m.%y'),user_id=user_id)


@main.route('/client/address/create', methods=['POST'])
def address_create():
	city = request.json.get('city')
	street = request.json.get('street')
	user_id = request.json.get('user_id')
	station = request.json.get('station')
	entrance = request.json.get('entrance')
	passcode = request.json.get('passcode')
	floor = request.json.get('floor')
	if not city or not street or not user_id:
		raise UException('Incorrect request: at least user_id, city and street required')
	client = Client.query.filter_by(user_id=user_id).first()
	if not client:
		raise UException('Incorrect user_id')
	try:
		address = Address(client.id, city, street, station, entrance, floor, passcode)
		db.session.add(address)
		db.session.commit()
	except ValueError as err:
		raise UException(message=err.message)
	except Exception, msg:
		raise UException(message='Unexpected server exception', status_code=500, payload=exc.message)
	return jsonify(status='created'), 201

@main.route('/client/address/update', methods=['PUT'])
def address_update():
	city = request.json.get('city')
	street = request.json.get('street')
	address_id = request.json.get('address_id')
	station = request.json.get('station')
	entrance = request.json.get('entrance')
	passcode = request.json.get('passcode')
	floor = request.json.get('floor')
	if not address_id:
		raise UException('Incorrect request: at least address_id required')
	address = Address.query.filter_by(id=address_id).first()
	if not address:
		raise UException('Incorrect address_id')
	try:
		if city is not None: address.city = city
		if street is not None: address.street = street
		if station is not None: address.station = station
		if entrance is not None: address.entrance = entrance
		if passcode is not None: address.passcode = passcode
		if floor is not None: address.floor = floor
		db.session.commit()
	except ValueError as err:
		raise UException(message=err.message)
	except Exception, msg:
		raise UException(message='Unexpected server exception', status_code=500, payload=exc.message)
	return jsonify(status='updated')

@main.route('/client/address/delete', methods=['DELETE'])
def address_delete():
	address_id = request.json.get('address_id')
	if not address_id:
		raise UException(message='Incorrect request')
	address = Address.query.filter_by(id=address_id).first()
	if not address:
		raise UException(message='Incorrect address_id')
	try:
		db.session.delete(address)
		db.session.commit()
	except:
		raise UException(message='Unexpected server exception', status_code=500)
	return jsonify(status='deleted')

@main.route('/client/address/list')
def get_client_addresses():
	user_id = request.args.get('user_id')
	if not user_id:
		raise UException('Incorrect query')
	client = Client.query.filter_by(user_id=user_id).first()
	if not client:
		raise UException('Incorrect user_id')
	data = list()
	try:
		addresses = client.address
		for addr in addresses:
			data.append({'address_id': addr.id,'city': addr.city, 'street':addr.street, 'station':addr.station, \
					'entrance':addr.entrance, 'passcode':addr.passcode, 'floor':addr.floor})
	except Exception, msg:
		UException(message=msg)
	return jsonify(address_list=data)

@main.route('/client/list')
def client_list():
	return jsonify(clients=Client.get_clients())


@main.route('/client/add/points', methods=['PUT'])
def client_add_points():
	user_id = request.json.get('user_id')
	points = request.json.get('points')
	if not user_id or not points:
		raise UException('Inocrrect request')
	client = Client.query.filter_by(user_id=user_id).first()
	if not client:
		raise UException('Incorrect request')
	try:
		client.points += float(points)
		db.session.commit()
	except Exception, msg:
		db.session.rollback()
		raise UException(message='Unexpected server exception', status_code=500, payload=exc.message)
	return jsonify(points=client.points)




