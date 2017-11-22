import json, os 
import uuid
from config import UPLOAD_FOLDER_IMG, UPLOAD_FOLDER_FILES
from app.utils import upload_image
from app.extensions import db
from sqlalchemy_mptt.mixins import BaseNestedSets



class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    price = db.Column(db.Numeric(10, 0))
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

    def __repr__(self):
        return self.name

    def __init__(self, name,  detail, is_avail, is_hot, is_new, category_id, number = None, price = '0'):
        self.name = name
        self.price = price
        self.number = price
        self.detail = detail
        self.is_avail = is_avail
        self.is_hot = is_hot
        self.is_new = is_new
        self.category_id = category_id 

    def save_product_images(self, files):
        path = os.path.join(UPLOAD_FOLDER_IMG,'products')
        for file in files: 
            name=str(uuid.uuid4())
            upload_image(path,file,name)
            db.session.add(ProductImage(name+'.jpeg', self.id))
        db.session.commit()

    def save_product_base_image(self, file): 
        path = os.path.join(UPLOAD_FOLDER_IMG,'products')
        upload_image(path,file,str(self.id))
        db.session.add(ProductImage(str(self.id)+'.jpeg', self.id, basic_image=True))
        db.session.commit()

    def get_base_image_url(self): 
        file = self.product_images.filter_by(product_id = self.id, basic_image = True ).first()
        if file:   
            return 'images/products/'+file.filename
        return  'images/no-image-available.png'

    #def get_gallery(self):
    #    files = self.product_images.all()
    #    print(files)





class Category(db.Model, BaseNestedSets):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    description = db.Column(db.Text())
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    # relations
    products = db.relationship(
        'Product', back_populates='category', lazy='dynamic')
    
    parent = db.relationship("Category", remote_side=[id], backref='child')

    category_image = db.relationship(
        'CategoryImage', back_populates='category', lazy='dynamic')

    def save_category_image(self, file):
        path = os.path.join(UPLOAD_FOLDER_IMG,'categories')
        upload_image(path,file,str(self.id))
        db.session.add(CategoryImage(str(self.id)+'.jpeg'))
        db.session.commit()

    @staticmethod
    def full_tree_as_list(parent_id=None):
        roots = Category.query.filter_by(parent_id=parent_id)
        full_tree = []
        for root in roots:
            full_tree.append(root.drilldown_tree()[0])
        return full_tree

    def __repr__(self):
        return self.name

    def __init__(self, parent_id, name, description=None):
        if parent_id :
            self.parent_id = int(parent_id) 
        self.name = name
        self.description = description
        



class ProductImage(db.Model):
    __tablename__ = 'product_images'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(80))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    basic_image = db.Column(db.Boolean, default=False)

    # relations
    product = db.relationship("Product", back_populates="product_images")

    def __repr__(self):
        return self.filename

    def __init__(self, name, product_id, basic_image=False):
        self.filename = name
        self.product_id = product_id
        self.basic_image = basic_image

class CategoryImage(db.Model):
    __tablename__ = 'category_images'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(80))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    # relations
    category = db.relationship("Category", back_populates="category_image")
    def __init__(self, id):
        self.filename = id 
        self.category_id = id

