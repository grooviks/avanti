from app import db
import json, os 
from config import UPLOAD_FOLDER_IMG, UPLOAD_FOLDER_FILES
#from app import constants as NET_TYPE

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    price = db.Column(db.Numeric(10, 2))
    number = db.Column(db.Integer)
    detail = db.Column(db.Text)
    tips = db.Column(db.Text)  # add for search speed
    is_avail = db.Column(db.Boolean, default=True)
    is_hot = db.Column(db.Boolean, default=False)
    is_new = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    # relations
    category = db.relationship("Category", back_populates="products")
    product_images = db.relationship(
        'ProductImage', back_populates='product', lazy='dynamic')

'''    def __init__(self, ip, id_network, owner = None, description = None,
        comment = None,  number = None, type = None):
        self.ip = ip
        self.id_network = id_network
        self.owner = owner
        self.description = description
        self.comment = comment
        self.number = number
        self.type = type '''

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    description = db.Column(db.Text())
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    # relations
    products = db.relationship(
        'Product', back_populates='category', lazy='dynamic')
    children = db.relationship(
    	"categories")
    category_image = db.relationship(
        'CategoryImage', back_populates='category', lazy='dynamic')

class ProductImage(db.Model):
    __tablename__ = 'product_images'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(80))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))

    # relations
    product = db.relationship("Product", back_populates="product_images")

class CategoryImage(db.Model):
    __tablename__ = 'catergory_images'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(80))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    # relations
    category = db.relationship("Category", back_populates="category_images")
