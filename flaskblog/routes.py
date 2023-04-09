import time, os
import secrets
from PIL import Image, UnidentifiedImageError
from flask import render_template, flash, redirect, url_for, request, abort, jsonify
from functools import wraps
from flaskblog import app, db,  bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, ProductForm, SearchForm
from flaskblog.models import *
from flaskblog.product_api import product_api
from flaskblog.cart_api import cart_api
from flaskblog.order_api import order_api
from flaskblog.category_api import category_api
from flaskblog.region_api import region_api
from flaskblog.brand_api import brand_api
from datetime import datetime, timedelta
from flask_login import login_user, current_user, logout_user, login_required, login_manager
from  werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
import json
from flask_httpauth import HTTPBasicAuth
from sqlalchemy import desc
import logging
from pathlib import Path
import traceback
import uuid
import random
from uuid import UUID
import PIL
from flaskblog.helper import *
import jwt
from flask import Response
from flask_cors import CORS, cross_origin

auth = HTTPBasicAuth()

@app.errorhandler(401)
def page_not_found(e):
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    return render_template('home.html', title='About Page')


@app.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    category_id = request.args.get('category_id', type=int)
    print(category_id)
    page = request.args.get('page', 1, type=int)
    
    if category_id:
        if current_user.role == UserRole.SUPERADMIN:
            products = Product.query.order_by(Product.id.desc()).filter(Product.category_id==category_id)
    
    elif current_user.role == UserRole.SUPERADMIN:
            products = Product.query.order_by(Product.id.desc())
        
    elif current_user.role == UserRole.ADMIN1:

        products = Product.query.join(User).filter(
            (User.id == current_user.id) | (User.parent == str(current_user.role))).order_by(Product.id.desc())
    elif current_user.role == UserRole.ADMIN2:
        products = Product.query.join(User).filter(
            (User.id == current_user.id) | (User.parent == str(current_user.role))).order_by(Product.id.desc())
           
    elif current_user.role == UserRole.ADMIN3:
        products = Product.query.join(User).filter(
            (User.id == current_user.id) | (User.parent == str(current_user.role))).order_by(Product.id.desc())
            
    else:
        products = Product.query.join(PostAccess).filter(
            PostAccess.user_id == current_user.id).order_by(Product.id.desc())
            

    #if request.method == 'POST':

    # title = request.form.get('title')
    # author = request.form.get('author')
    # date = request.form.get('date_posted')
    # if title:
    #     products = products.filter(db.func.lower(
    #         Product.title).like('%' + title + '%'))
    # if date:
    #     date_posted = datetime.strptime(date, "%d/%m/%Y")
    #     products = products.filter(Product.date_posted == date_posted)
    # if author:
    #     author = User.query.filter(db.func.lower(
    #         User.username).like('%' + author + '%')).all()
    #     products = products.filter(Product.user_id.in_([x.id for x in author]))
        
    products = products.paginate(page=page, per_page=8)
    
    # for i in products:
    #     print(i.author)
    return render_template('products.html', products=products)


@app.route('/about')
@login_required
def about():
    return render_template('about.html', title='About Page')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            app.logger.info('%s logged in successfully', user.username)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            app.logger.info('%s logged in FAIL!', form.username.data)
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/api/v1/login", methods=['POST'])
def api_login():
    print(request)
    # creates dictionary of form data
    auth = request.json
    print(auth)
    if not auth or not auth.get('email') or not auth.get('password'):
        # returns 401 if any email or / and password is missing
        return Response('Could not verify', mimetype="application/json", status=401) 
   
    user = Users.query\
        .filter_by(email = auth.get('email'))\
        .first()
   
    if not user:
        # returns 401 if user does not exist
        return Response('Could not verify', mimetype="application/json", status=401) 
    print(user.username)
    if bcrypt.check_password_hash(user.password, auth.get('password')):
        print("if bcrypt")
        # generates the JWT Token
        token = jwt.encode({
            'public_id': user.public_id,
            'exp' : datetime.utcnow() + timedelta(minutes = 120)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        i_dict = {}
        i_dict["username"] = user.username
        i_dict["userRole"] = str(user.role)
        i_dict["email"] = user.email
        i_dict["phone"] = user.phone_number
        i_dict["address"] = user.address
        i_dict["token"] = token.decode('utf-8')
        print(i_dict)
        return Response(json.dumps(i_dict), mimetype="application/json", status=201)    
    # returns 403 if password is wrong
    return Response('Could not verify', mimetype="application/json", status=403)             


# signup route
@app.route('/api/v1/signup', methods =['POST'])
def api_signup():
    # creates a dictionary of the form data
    data = request.form
   
    # gets name, email and password
    name, email, phone_number, role, parent = data.get('name'), data.get('email'), data.get('phone'), data.get('role'), data.get('parent'), 
    password = data.get('password')
   
    # checking for existing user
    user = Users.query\
        .filter_by(email = email)\
        .first()
    if not user:
        # database ORM object
        user = Users(
            public_id = str(uuid.uuid4()),
            username = name,
            email = email,
            phone_number = phone_number,
            role = role, 
            parent= parent,
            password = bcrypt.generate_password_hash(password).decode('utf-8')
        )
        # insert user
        db.session.add(user)
        db.session.commit()
   
        return Response("sucsessfully registered", mimetype="application/json", status=201)            
    else:
        # returns 202 if user already exists
        return Response("user already exists", mimetype="application/json", status=202)             

@app.route("/api/v1/profile", methods=['PUT'])
def api_profile():
    try:
        print('profile')
    except Exception as e:
        app.logger.info('api_category_new error: %s', str(e)) 
        error = traceback.format_exc()
        print(error)
        return Response("bad request", mimetype="application/json", status=400)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():

    if current_user.role == UserRole.SUPERADMIN:
        child = Users.query.all()
    elif current_user.role == UserRole.ADMIN1:
        child = Users.query.filter_by(parent='admin1').all()
    elif current_user.role == UserRole.ADMIN2:
        child = Users.query.filter_by(parent='admin2').all()
    elif current_user.role == UserRole.ADMIN3:
        child = Users.query.filter_by(parent='admin3').all()
    else:
        child = None
    userrole = UserRole.SUPERADMIN
    return render_template('account.html', title='Account', child=child, userrole=userrole)

@app.route("/categories", methods=['GET'])
@login_required
def categories():
    if request.method == 'GET':
        categories = Category.query.order_by(Category.id.desc())
        return render_template('categories.html', title='Categories',
                            legend='Categories', categories=categories)


@app.route("/category/new", methods=['GET', 'POST'])
@login_required
def new_category():
    if request.method == 'GET':
        categories = Category.query.order_by(Category.id.desc())
        return render_template('create-category.html', title='New Category',
                            legend='New Category', categories=categories)
    if  request.method == 'POST':
        try:
            path_image='/static/cat_image/'
            cat_id = random.randint(10, 50)
            category_name_tm =  request.form.get('category_name_tm')
            category_name_ru =  request.form.get('category_name_ru')
            parent_category =  request.form.get('parent_category')
            picture_file = request.files['picture_file']
            icon_file = request.files['icon_file']
            category_image = save_picture(picture_file, path_image)
            category_image =path_image + category_image
            category_icon = save_picture(icon_file, path_image)
            category_icon = path_image + category_icon
            category = Category(id = cat_id, category_name_tm=category_name_tm, category_name_ru=category_name_tm, parent_category=parent_category, 
                        category_image=category_image, category_icon=category_icon)
            db.session.add(category)
            db.session.commit()
            flash('category created success', 'success')
            return render_template('create-category.html', title='New Category',
                            legend='New Category')
        except:
            flash('Error on adding category', 'danger')
            return render_template('create-category.html', title='New Category',
                            legend='New Category')

@app.route("/product/new", methods=['GET', 'POST'])
@login_required
def new_product():
    form = ProductForm()
    if request.method == 'GET':
        categories = Category.query.order_by(Category.id.desc())
        return render_template('create_product.html', title='New Product',
                           form=form, legend='New Product', categories=categories)
        
    if form.validate_on_submit() and request.method == 'POST':
      print("hi")
      print(form.picture.data)  
      try:
        if form.picture.data:
            path_l="/static/product_photo"
            path_s="/static/product_photo_small"
            picture_files = []
            for picture_file in form.picture.data:
                picture_file = save_picture(picture_file, path_l)
                picture_files.append(path_l + time.strftime("/%Y/%m/%d/") + picture_file)
            small_image = save_picture_small(form.picture.data[0], path_s)
            product_image = (path_s + time.strftime("/%Y/%m/%d/") + small_image) 
        state=True 
        category =  request.form.get('category')
        print('cat2:'+ category)
        product = Product(product_name=form.product_name.data, description_tm=form.description_tm.data, description_ru=form.description_ru.data, author=current_user, large_name=picture_files, region_id=1, small_name=product_image, language=form.language.data, price=form.price.data, quantity=form.quantity.data, category_id=category)
        db.session.add(product)
        db.session.commit()
        product_access = ProductAccess(user_id=current_user.id, product_id=product.id)
        db.session.add(product_access)
        db.session.commit()
        app.logger.info('%s product created successfully', current_user.username)
        flash('Your product has been created!', 'success')
        return redirect(url_for('products'))
      except IntegrityError:
        db.session.rollback()
        error = traceback.format_exc()
        print(error)
        flash('Duplicated titles!', 'danger')
      except UnidentifiedImageError:
        flash('Please upload only image file!', 'danger')
      except ValueError:
        flash('Please check values!', 'danger')         
      except Exception as e:
        error = traceback.format_exc()  
        flash('Error', 'danger')
        app.logger.info('Error occured: %s', str(error))
        print(error)
    return render_template('create_product.html', title='New Product',
                           form=form, legend='New Product')



@app.route("/create_user", methods=['GET', 'POST'])
# @login_required
def create_user():
    # if (current_user.role != UserRole.SUPERADMIN):
    #     abort(403)
    form = RegistrationForm()
    if form.validate_on_submit():

        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        role_select = request.form.get('role_select')
        parent_select = request.form.get('parent_select')
        role_enum = UserRole.from_string(role_select)
        if role_enum:

            user = Users(username=form.username.data, password=hashed_password,
                        role=role_enum, parent=parent_select)

            db.session.add(user)
            db.session.commit()
            # app.logger.info('%s created successfully user: %s ',
            #                 current_user.username, user.username)
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))
        else:
            flash('Check columns!', 'danger')
    return render_template('create_user.html', title='Register', form=form)


@app.route("/product/<int:product_id>")
@login_required
def product(product_id):
    product = Product.query.get_or_404(product_id)
    if (product.author != current_user and current_user.role != UserRole.SUPERADMIN and current_user.role != UserRole.ADMIN):
        abort(403)
    images = list(product.large_name.strip('{}').split(","))
    return render_template('product.html', title=product.product_name, product=product, images=images)


@app.route("/product/<int:product_id>/update", methods=['GET', 'POST'])
@login_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    if (product.author != current_user and current_user.role != UserRole.SUPERADMIN and current_user.role != UserRole.ADMIN):
        abort(403)
    form = PostForm()
    if request.method == 'POST' and form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
        product.title = form.title.data
        product.content = form.content.data
        product.image_file = picture_file
        product.date_posted = form.date_posted.data
        product.language = form.language.data
        product.category = form.category.data
        db.session.commit()
        app.logger.info('%s product updated successfully product:  %s',
                        current_user.username, product.title)
        flash('Your product has been updated!', 'success')
        return redirect(url_for('product', product_id=product.id))
    elif request.method == 'GET':
        form.title.data = product.title
        form.content.data = product.content
        form.picture.data = product.image_file
        form.date_posted.data = product.date_posted
        form.language.data = product.language
        form.category.data = product.category
    return render_template('update_product.html', title='Update Product',
                           form=form, legend='Update Product', product=product)


@app.route("/product/<int:product_id>/delete", methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if (product.author != current_user and current_user.role != UserRole.SUPERADMIN and current_user.role != UserRole.ADMIN):
        abort(403)
    db.session.delete(product)
    db.session.commit()
    app.logger.info('%s product deleted successfully product:  %s',
                    user.username, product.title)
    flash('Your product has been deleted!', 'success')
    return redirect(url_for('products'))


@app.route("/product/<int:product_id>/activate_product", methods=['GET', 'POST'])
@login_required
def activate_product(product_id):
    product = Product.query.get_or_404(product_id)
    if (product.author != current_user and current_user.role != UserRole.SUPERADMIN and current_user.role != UserRole.ADMIN):
        abort(403)
    form = ProductForm()
    is_active_str = request.form.get("is_active")
    is_active = False
    if is_active_str:
      if is_active_str.lower() == "true":
        is_active = True
        flash('Your product has been activated!', 'success')
      else:
        flash('Your product has been disabled!', 'success')
    product.state = is_active
    db.session.commit()
    app.logger.info('%s changed product: %s status to :  %s',
                    user.username, product.product_name, product.state)
    return redirect(request.referrer)

@app.route("/orders", methods=['GET'])
def orders():
    result = []
    order_query = db.session.query(Order, User).join(User, Order.user_id == User.id).order_by(Order.id.desc()).all()
    for i in order_query:
        result_order ={}
        result_order["order"] = i
        order_items = db.session.query(OrderItem, Product).join(Product, OrderItem.product_id == Product.id).filter(OrderItem.order_id==i[0].id).order_by(OrderItem.id.desc()).all()
        result_order["order_items"] = order_items
        result.append(result_order)
    return render_template('orders.html', title='Orders',
                           result=result)


#---------------------------- Blueprint API here-------------------------------------------

# product api here
app.register_blueprint(product_api)
# cart api here
app.register_blueprint(cart_api)
# order api here
app.register_blueprint(order_api)
# category api here
app.register_blueprint(category_api)
# region api here
app.register_blueprint(region_api)
# brand api here
app.register_blueprint(brand_api)




@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.errorhandler(403)
def cant_permission(e):
    # note that we set the 404 status explicitly
    return render_template('403.html'), 403
