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
    price = StringField('price', validators= [DataRequired()])
    number = StringField('number')
    detail = TextAreaField('detail')
    tips = TextAreaField('tips')  # add for search speed
    is_avail = BooleanField('is_avail')
    is_hot = BooleanField('is_hot')
    is_new = BooleanField('is_new')
    category = SelectField('category',choices=[(str(c.id), c.name) for c in Category.query.order_by('name')])


class CategoryForm(Form):
    name = StringField('name', validators= [DataRequired()])
    parent = SelectField('parent')
    image = FileField('image')
    description = TextAreaField('description')

    def __init__(self,*args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        choices_categories = [(str(c.id), c.name) for c in Category.query.order_by('name')]
        choices_categories.append(('', 'Нет'))
        self.parent.choices = choices_categories


class ProductImageForm(Form):
    image = FileField('Image File')



class ProductImagesForm(Form):
    images = FileField('Image File')