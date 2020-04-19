from flask import Flask, redirect, url_for
from flask_markdown import markdown
from .extensions import db, login_manager
from .errors import not_found_error, internal_error


def application():
	app = Flask(__name__)
	app.config.from_object('config')

	db.init_app(app)
	db.app = app
	markdown(app)
	register_blueprints(app)
	app.register_error_handler(404, not_found_error)
	app.register_error_handler(500, internal_error)
	# register_debug(app)
	# register_database(app)
	# register_jinja2_extension(app)
	# register_upload(app)
	init_login(app)
	return app


def register_blueprints(app):
	"""Configure blueprints in views."""
	from .admin import admin
	from .frontend import frontend
	# from api import api
	for bp in [admin, frontend]:
		app.register_blueprint(bp)


def init_login(app):
	login_manager.init_app(app)
	@login_manager.user_loader
	def load_user(userid):
		from avanti.app.admin import User
		return User.query.get(userid)

	def unauthorized():
		return redirect(url_for('admin.login'))
	login_manager.unauthorized = unauthorized
