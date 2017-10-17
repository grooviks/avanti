from flask import Blueprint, render_template, current_app, request, flash, \
    url_for, redirect, session, abort

from app.frontend import Product, Category
from .forms import ProductForm, CategoryForm, ProductImageForm, ProductImagesForm
from app.extensions import db

admin = Blueprint('admin', __name__, url_prefix='/admin', static_folder='static')

@admin.route('/')
@admin.route('/index')
def index():
	#if current_user.is_authenticated:
    #    return redirect(url_for('user.profile'))
    return render_template('admin/index.html')

@admin.route('/manage_products')
def manage_product():
	#products = Product.query.all()
	return render_template('admin/manage_products.html')

@admin.route('/manage_categories')
def manage_categories():
	#categories = Category.query.all()
	roots = Category.query.filter_by(parent_id=None)
	full_tree = []
	for root in roots:
		full_tree.append(root.drilldown_tree()[0])
	print(full_tree)
	return render_template('admin/manage_categories.html', 
		category=full_tree)

@admin.route('/product/<id>', methods = ['GET', 'POST'])
def product(id):
	#product = Product.query.filter_by(id = id).first()
	return render_template('admin/product.html')

@admin.route('/category/<id>', methods = ['GET', 'POST'])
def category(id):
	cat = Category.query.filter_by(id = id).first()
	return render_template('admin/category.html')

@admin.route('/new_product', methods = ['GET', 'POST'])
def new_product():
	return render_template('admin/new_product.html')


@admin.route('/new_category', methods = ['GET', 'POST'])
def new_category():
	form = CategoryForm()
	if form.validate_on_submit():
		category = Category(name = form.name.data,
					description = form.description.data,
					parent_id = form.parent.data)
		db.session.add(category)
		db.session.commit()
		if form.image.data:
			category.save_category_image(form.image.data)
		flash('Категория добавлена!!! ', 'success')
		return redirect(url_for('admin.manage_categories'))
	elif request.method == 'POST':        
		flash('Не заполнены обязательные поля!!! ', 'warning')
	return render_template('admin/new_category.html',
		form = form)


