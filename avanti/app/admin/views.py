from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_user, logout_user, login_required

from avanti.app.extensions import db
from avanti.app.frontend import Product, Category
from avanti.app.utils import decrypt
from .forms import ProductForm, CategoryForm, ProductImageForm, ProductImagesForm, LoginForm, UserForm, EditUserForm
from .models import User

admin = Blueprint('admin', __name__, url_prefix='/admin', static_folder='static')


@admin.route('/')
@admin.route('/index')
@login_required
def index():
    # if current_user.is_authenticated:
    #    return redirect(url_for('user.profile'))
    return render_template('admin/index.html')


@admin.route('/manage_products')
@login_required
def manage_products():
    products = Product.query.all()

    return render_template('admin/manage_products.html',
                           products=products)


@admin.route('/manage_categories')
@login_required
def manage_categories():
    return render_template('admin/manage_categories.html',
                           category=Category.full_tree_as_list())


@admin.route('/product/<id>', methods=['GET', 'POST'])
@login_required
def product(id):
    product = Product.query.filter_by(id=id).first_or_404()
    form = ProductForm(obj=product)
    # подставляем дефолтное значение для select_field
    form.category.process_data(product.category_id)
    base_img_form = ProductImageForm()
    images_form = ProductImagesForm()

    if form.is_submitted():
        if request.form['submit'] == 'Изменить':
            product.name = form.name.data
            product.price = form.price.data
            product.category_id = get_really_data(form.category)
            product.detail = form.detail.data
            product.is_avail = form.is_avail.data
            product.is_hot = form.is_avail.data
            product.is_new = form.is_avail.data
            db.session.commit()
            if base_img_form.image.data:
                product.delete_product_images(basic_image=True)
                product.save_product_base_image(base_img_form.image.data)
            if 'images' in request.files:
                files = request.files.getlist("images")
                product.save_product_images(files)
        elif (request.form['submit'] == 'Удалить'):
            product.delete_product_images()
            db.session.delete(product)
            db.session.commit()
            flash('Удалено!!! ', 'success')
            return redirect(url_for('admin.manage_products'))
        else:
            flash('Ошибка редактирования!!! ', 'danger')
        return redirect(url_for('admin.manage_products'))

    return render_template('admin/product.html',
                           product=product,
                           form=form)


@admin.route('/category/<id>', methods=['GET', 'POST'])
@login_required
def category(id):
    cat = Category.query.filter_by(id=id).first_or_404()
    form = CategoryForm(obj=cat)
    if form.validate_on_submit():
        if request.form['submit'] == 'Изменить':
            cat.name = form.name.data,
            cat.description = form.description.data,
            # cat.parent_id = form.parent.data
            db.session.commit()
            if form.image.data:
                cat.delete_category_image()
                cat.save_category_image(form.image.data)
        elif (request.form['submit'] == 'Удалить'):
            cat.delete_category_image()
            db.session.delete(cat)
            db.session.commit()
            flash('Удалено!!! ', 'success')
            return redirect(url_for('admin.manage_categories'))
        else:
            flash('Ошибка редактирования!!! ', 'danger')
        return redirect(url_for('admin.category', id=cat.id))
    # image in product.product_images.all()
    return render_template('admin/category.html',
                           form=form,
                           category=cat)


@admin.route('/new_product', methods=['GET', 'POST'])
@login_required
def new_product():
    form = ProductForm()
    base_img_form = ProductImageForm()
    images_form = ProductImagesForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            price=form.price.data,
            category_id=form.category.data,
            detail=form.detail.data,
            is_avail=form.is_avail.data,
            is_hot=form.is_avail.data,
            is_new=form.is_avail.data
        )
        db.session.add(product)
        db.session.commit()

        if base_img_form.image.data:
            product.save_product_base_image(base_img_form.image.data)
        if request.files['images'].filename:
            files = request.files.getlist("images")
            product.save_product_images(files)
        flash('Продукт добавлен!!! ', 'success')
        return redirect(url_for('admin.manage_products'))
    elif request.method == 'POST':
        flash('Не заполнены обязательные поля!!! ', 'warning')
    return render_template('admin/new_product.html',
                           form=form,
                           base_img_form=base_img_form,
                           images_form=images_form)


@admin.route('/new_category', methods=['GET', 'POST'])
@login_required
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data,
                            description=form.description.data,
                            parent_id=form.parent.data)
        db.session.add(category)
        db.session.commit()
        if form.image.data:
            category.save_category_image(form.image.data)
        flash('Категория добавлена!!! ', 'success')
        return redirect(url_for('admin.manage_categories'))
    elif request.method == 'POST':
        flash('Не заполнены обязательные поля!!! ', 'warning')
    return render_template('admin/new_category.html',
                           form=form)


@admin.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember_me = form.remember_me.data
        user = User.query.filter_by(username=username).first()
        if user:
            if decrypt(password, user.password):
                login_user(user, remember=remember_me)
                return redirect(url_for('admin.index'))
            else:
                flash('Неверный пароль!!', 'warning')
        else:
            flash('Пользователь не существует!', 'warning')
    return render_template('admin/login.html',
                           form=form)


@admin.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))


@admin.route('/new_user', methods=['GET', 'POST'])
@login_required
def new_user():
    form = UserForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    password=form.password.data,
                    email=form.email.data,
                    full_name=form.full_name.data,
                    phone=form.phone.data,
                    status=form.status.data,
                    role=form.role.data)
        db.session.add(user)
        db.session.commit()
    return render_template('admin/new_user.html',
                           form=form)


@admin.route('/manage_users', methods=['GET', 'POST'])
@login_required
def manage_users():
    return render_template('admin/manage_users.html',
                           users=User.query.all())


@admin.route('/user/<int:id>', methods=['GET', 'POST'])
@login_required
def user(id):
    user = User.query.filter_by(id=id).first()
    form = EditUserForm(obj=user)
    if form.validate_on_submit():
        if request.form['submit'] == 'Изменить':
            user.username = form.username.data
            user.email = form.email.data
            user.full_name = form.full_name.data
            user.phone = form.phone.data
            user.status = form.status.data
            user.role = form.role.data
            db.session.commit()
            flash('Пользователь изменен!!', 'success')
        elif request.form['submit'] == 'Удалить':
            db.session.delete(user)
            db.session.commit()
            flash('Удалено!!! ', 'success')
            return redirect(url_for('admin.manage_users'))
        else:
            flash('Ошибка редактирования!!! ', 'danger')
    return render_template('admin/user.html',
                           user=user,
                           form=form)

# FIXME: не работает нормально default value в поле
def get_really_data(field):
    try:
        return field.raw_data[0]
    except IndexError:
        return field.data
