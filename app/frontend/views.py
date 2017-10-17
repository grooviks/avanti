from flask import Blueprint, render_template, current_app, request, flash, \
    url_for, redirect, session, abort
from .models import Category, Product
#from flask import render_template, flash, redirect, url_for, request, json
#from app import app, db
#from app.forms import AddSpareForm, SearchForm, AddNetworkForm, DeviceForm, ServerForm
#from app.models import spares, networks, devices, persons, company, servers
#from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER_IMG, UPLOAD_FOLDER_FILES

frontend = Blueprint('frontend', __name__,)

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