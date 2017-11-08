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
def manage_products():
	products = Product.query.all()

	return render_template('admin/manage_products.html', 
		products=products)

@admin.route('/manage_categories')
def manage_categories():
	return render_template('admin/manage_categories.html', 
		category=Category.full_tree_as_list())

@admin.route('/product/<id>', methods = ['GET', 'POST'])
def product(id):
	#product = Product.query.filter_by(id = id).first()
	return render_template('admin/product.html')

@admin.route('/category/<id>', methods = ['GET', 'POST'])
def category(id):
	cat = Category.query.filter_by(id = id).first()
	form = CategoryForm(obj=cat)
	#print(cat.name, cat.parent, cat.category_image)
	if form.validate_on_submit():
		if 	request.form['submit'] == 'Изменить':
			cat.name = form.name.data,
			cat.description = form.description.data,
			#cat.parent_id = form.parent.data
			db.session.commit()
			if form.image.data:
				cat.save_category_image(form.image.data)
		elif (request.form['submit'] == 'Удалить'):
			db.session.delete(cat)
			db.session.commit()
			flash('Удалено!!! ', 'success')
			return redirect(url_for('admin.manage_categories'))
		else:
			flash('Ошибка редактирования!!! ', 'danger')
		return redirect(url_for('admin.category', id = cat.id))
	#image in product.product_images.all()
	return render_template('admin/category.html', 
		form = form,
		category = cat)

@admin.route('/new_product', methods = ['GET', 'POST'])
def new_product():
	form=ProductForm()
	base_img_form=ProductImageForm()
	images_form=ProductImagesForm()
	if form.validate_on_submit():
		print(form.detail.data)
		product = Product(    
				name = form.name.data,
    			price = form.price.data,
    			number = form.number.data,
    			category_id = form.category.data,
    			detail = form.detail.data,
    			is_avail = form.is_avail.data,
    			is_hot = form.is_avail.data,
    			is_new = form.is_avail.data
			)
		db.session.add(product)
		db.session.commit()
		if base_img_form.image.data:
			product.save_product_base_image(base_img_form.image.data)
			print(base_img_form.image.data)
		if images_form.images.data:
			product.save_product_images(images_form.images.data)
			print(images_form.images.data)
		flash('Продукт добавлен!!! ', 'success')
		return redirect(url_for('admin.manage_products'))
	elif request.method == 'POST': 
		flash('Не заполнены обязательные поля!!! ', 'warning')
	return render_template('admin/new_product.html', 
		form=form, 
		base_img_form=base_img_form, 
		images_form=images_form)


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


