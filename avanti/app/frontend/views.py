from flask import Blueprint, render_template, current_app, request, flash, \
    url_for, redirect, session, abort, send_from_directory
from .models import Category, Product
#from flask import render_template, flash, redirect, url_for, request, json
#from app import app, db
#from app.forms import AddSpareForm, SearchForm, AddNetworkForm, DeviceForm, ServerForm
#from app.models import spares, networks, devices, persons, company, servers
#from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER_IMG, UPLOAD_FOLDER_FILES

frontend = Blueprint('frontend', __name__, static_folder='static')

@frontend.route('/')
@frontend.route('/index')
def index():
	return render_template('index.html')


@frontend.route('/about_us')
def about_us():
	return render_template('about_us.html')

@frontend.context_processor
def categories_parent_list():
	return {"cat_list":[c for c in Category.query.filter_by(parent_id=None)]}

@frontend.route('/categories')
def categories():
	return render_template('categories.html')


@frontend.route('/category/<int:id>')
def category(id):
	cat = Category.query.filter_by(id=id).first_or_404()
	roots=cat.path_to_root().all()
	roots.reverse()

	if cat.child:
		return render_template('category.html',
							   category=cat,
							   roots=roots)
	else:
		prod=Product.query.filter_by(category_id=cat.id).all()
		return render_template('products.html',
							   category=cat,
							   products=prod,
							   roots=roots)
	#roots = Category.query.all()
	#for root in roots:
	#print(cat.drilldown_tree()[0])


@frontend.route('/contacts')
def contacts():
	return render_template('contacts.html')


@frontend.route('/services')
def services():
	return render_template('services.html')


@frontend.route('/payment')
def payment():
	return render_template('payment.html')


@frontend.route('/product/<int:id>')
def product(id):
	prod=Product.query.filter_by(id=id).first_or_404()
	return render_template('product.html',
						   product=prod)

#@frontend.route('get_image_category')
#def get_image_category(id):#
	#pass

@frontend.route('/robots.txt')
def static_from_root():
	return send_from_directory(current_app.static_folder, request.path[1:])
