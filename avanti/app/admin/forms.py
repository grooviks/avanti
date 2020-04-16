from flask_wtf import  Form
from wtforms import StringField, BooleanField, SelectField, TextAreaField, FileField, PasswordField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo
#from flask_wtf.file import FileField, FileAllowed, FileRequired
from avanti.app.frontend.models import Category
from avanti.app import constants as USER


class ProductForm(Form):
    name = StringField('name', validators= [DataRequired()])
    price = StringField('price')
    number = StringField('number')
    detail = TextAreaField('detail')
    tips = TextAreaField('tips')  # add for search speed
    is_avail = BooleanField('is_avail')
    is_hot = BooleanField('is_hot')
    is_new = BooleanField('is_new')
    category = SelectField('category')

    def __init__(self,*args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        '''
        адская хуйня для создания selectfield с удобным отображением в виде дерева, переписать! 
        cat1
        --- cat2
        --- cat3 
        ------ cat4
        cat5 
        cat6 
        --- cat7

        '''
        def child_print(item, choices_categories, lv=1):
            if item.get('children'):
                for ch in item['children']:
                    #print(lv*'---', ch['node'])
                    choices_categories.append((str(ch['node'].id), (lv*'---'+' '+ch['node'].name)))
                    child_print(ch, choices_categories, lv+1)

        choices_categories = []
        for item in Category.full_tree_as_list():
           #print(item['node'])
           choices_categories.append((str(item['node'].id), item['node'].name))
           child_print(item, choices_categories)

        self.category.choices = choices_categories


class CategoryForm(Form):
    name = StringField('name', validators= [DataRequired()])
    parent = SelectField('parent')
    image = FileField('image')
    description = TextAreaField('description')

    def __init__(self,*args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        '''
        адская хуйня для создания selectfield с удобным отображением в виде дерева, переписать! 
        cat1
        --- cat2
        --- cat3 
        ------ cat4
        cat5 
        cat6 
        --- cat7

        '''
        def child_print(item, choices_categories, lv=1):
            if item.get('children'):
                for ch in item['children']:
                    #print(lv*'---', ch['node'])
                    choices_categories.append((str(ch['node'].id), (lv*'---'+' '+ch['node'].name)))
                    child_print(ch, choices_categories, lv+1)

        choices_categories = [('', 'Нет')]
        for item in Category.full_tree_as_list():
           choices_categories.append((str(item['node'].id), item['node'].name))
           child_print(item, choices_categories)

        self.parent.choices = choices_categories


class ProductImageForm(Form):
    image = FileField('ImageFile')


class ProductImagesForm(Form):
    images = FileField('ImageFiles')

class LoginForm(Form):
    username = StringField('username',validators=[DataRequired()])
    password = PasswordField('password',validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default = False)

class UserForm(Form):
    username = StringField('username',validators=[DataRequired()], render_kw={ 'placeholder': 'Имя пользователя' })
    password = PasswordField('password',validators=[DataRequired(), EqualTo('password_confirm', message = 'Пароли не совпадают' ), Length(6.20) ], render_kw={ 'placeholder': 'Пароль' } )
    email = StringField('email', validators=[DataRequired(), Email()], render_kw={ 'placeholder': 'E-Mail' } )
    password_confirm = PasswordField('repeat password', render_kw={ 'placeholder': 'Повтор пароля' })
    full_name = StringField('full_name', validators=[Length(0, 64)], render_kw={ 'placeholder': 'ФИО' })
    phone = StringField('phone', render_kw={ 'placeholder': 'Телефон' })
    status = RadioField(choices=USER.STATUS.items(), default='2')
    role = RadioField(choices=USER.ROLE.items(), default='2')

class EditUserForm(Form):

    username = StringField('username',validators=[DataRequired()], render_kw={ 'placeholder': 'Имя пользователя' })
    email = StringField('email', validators=[DataRequired(), Email()], render_kw={ 'placeholder': 'E-Mail' } )
    full_name = StringField('full_name', validators=[Length(0, 64)], render_kw={ 'placeholder': 'ФИО' })
    phone = StringField('phone', render_kw={ 'placeholder': 'Телефон' })
    status = RadioField(choices=USER.STATUS.items())
    role = RadioField(choices=USER.ROLE.items())

