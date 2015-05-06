from . import db
from werkzeug.security import generate_password_hash, check_password_hash
import re
from sqlalchemy.orm import validates
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app

class Permission:
	MAKE_ORDER = 0x01
	SAVE_POINTS = 0x02
	CREATE_MENU = 0x04
	CONFIRM_ORDER = 0x08
	ADMINISTER = 0x80

class UserConfig:
	MIN_PASSW_LEN = 6
	MAX_PASSW_LEN = 64
	EMAIL_LEN = 64
	CONF_EXP_TIME = 3600

class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	permissions = db.Column(db.Integer)
	users = db.relationship('User', backref='role', lazy='dynamic')

	@staticmethod
	def insert_roles():
		roles = {
			'Client' : Permission.MAKE_ORDER | Permission.SAVE_POINTS,
			'Manager' : Permission.CREATE_MENU | Permission.CONFIRM_ORDER,
			'Administrator' : Permission.ADMINISTER
		}
		for r in roles:
			role = Role.query.filter_by(name=r).first()
			if role is None:
				role = Role(name=r)
			role.permissions = roles[r]
			db.session.add(role)
		db.session.commit()

	@staticmethod
	def get_admin_id():
		admin = Role.query.filter_by(name='Administrator').first()
		if admin: result = admin.id
		else: result = None
		return result


	def __repr__(self):
		return '<Role: id = %d, name = %s' % (self.id, self.name)

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(UserConfig.EMAIL_LEN), unique=True)
	password_hash = db.Column(db.String(128))
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
	confirmed = db.Column(db.Boolean, nullable=False, default=False)


	@staticmethod
	def get_users(role_name):
		result = dict()
		role = Role.query.filter_by(name=role_name).first()
		#user_id_list = []
		user_list = []
		if role:
			users = User.query.filter_by(role_id=role.id).all()
			for user in users:
				user_list.append({'email':user.email, 'user_id': user.id})
				#user_id_list.append(user.id)
		#result['user_id_list'] = user_id_list
		#result['user_list'] = user_list
		result = user_list
		return result


	def get_role_name(self):
		role = Role.query.filter_by(id=self.role_id).first()
		return role.name

	@staticmethod
	def admin_init():
		admin_id = Role.get_admin_id()
		if admin_id:
			if not User.query.filter_by(role_id=admin_id).first():
				db.session.add(User('admin@m.ru', '123456', 'Administrator'))
				db.session.commit()
	@staticmethod
	def admin():
		admin_id = Role.get_admin_id()
		admin = User.query.filter_by(role_id=admin_id).first()
		return admin


	@validates('email')
	def validate_email(self, key, value):
		user = User.query.filter_by(email=value).first()
		if user is not None and user is not self:
			raise ValueError('Email already exists')
		if not re.match(r'[^@]+@[^@]+\.[^@]+', value):
			raise ValueError('Incorrect email format')
		return value

	@validates('role_id')
	def validate_role(self, key, value):
		role = Role.query.filter_by(id=value).first()
		if role is None:
			raise ValueError('Incorrect role identifier')
		return value

	@validates('password_hash')
	def validate_password(self, key, value):
		if len(value) < UserConfig.MIN_PASSW_LEN or len(value) > UserConfig.MAX_PASSW_LEN:
			raise ValueError('Incorrect password length (minimal length = %d, maximal length = %d)'%(UserConfig.MIN_PASSW_LEN, UserConfig.MAX_PASSW_LEN))
		return generate_password_hash(value)


	def __init__(self, email, password, role_name):
		self.email = email
		self.password_hash = password
		role = Role.query.filter_by(name=role_name).first()
		if role is None:
			raise ValueError('Incorrect role name')
		self.role_id = role.id

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	'''def generate_confirmation_token(self, expiration=UserConfig.CONF_EXP_TIME):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'confirm' : self.id})

	def confirm_token(self):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('confirm') != self.id:
			result =  False
		else:
			self.confirmed = True
			result = True
		return result'''

	def __repr__(self):
		return '<User: email: %s, phash: %s, role_id: %d' % (self.email, self.password_hash, self.role_id)
