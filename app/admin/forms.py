from flask_wtf import  Form
from app.extensions import db
from wtforms.ext.sqlalchemy.fields import QuerySelectField
#import FlaskForm
from wtforms import StringField, BooleanField, SelectField, TextAreaField, IntegerField,  SubmitField, FileField
from wtforms.validators import DataRequired, optional, length, NumberRange
from wtforms.widgets import TextArea, Input
#from flask_wtf.file import FileField, FileAllowed, FileRequired
from app.frontend import Product, Category



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