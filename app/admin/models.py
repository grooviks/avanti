from app.extensions import db
from datetime import datetime
from app import constants as USER
from app.utils import encrypt


class User(db.Model):
	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	full_name = db.Column(db.String(200))
	email = db.Column(db.String(100), nullable=False)
	password = db.Column(db.String(255), nullable=False)
	role = db.Column(db.Integer, default=USER.USER )
	status = db.Column(db.Integer, default=USER.ACTIVE )
	#token = db.Column(db.String(255), nullable=False)
	birth_date = db.Column(db.DateTime, nullable=True)
	phone = db.Column(db.String(20))
	reg_date = db.Column(db.DateTime, default=datetime.now)
	
	# Flask-Login integration
	def is_authenticated(self):
		return True
	
	def is_active(self):
		return True
	
	def is_anonymous(self):
		return False
	
	def get_id(self):
		return self.id

	@property
	def get_status(self): 
		return USER.STATUS[str(self.status)]

	@property
	def get_role(self):
		return USER.ROLE[str(self.role)]


		
    # relations
    # в дальнейшем для заказов и адресов пользователей
    #orders = db.relationship('Order', back_populates='user', lazy='dynamic')
    #user_addresses = db.relationship(
    #    'UserAddress', back_populates='user', lazy='dynamic')
    
	def __init__(self, username,  full_name, email, password, phone, role = USER.USER, status = USER.ACTIVE):
		self.username = username.strip()
		self.full_name = full_name
		self.email = email.strip()
		self.password = encrypt(password)
		self.phone = phone
		self.role = role
		self.status = status

	def __repr__(self):
		return self.username