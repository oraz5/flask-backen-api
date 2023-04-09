from flaskblog import app, db, bcrypt
from flask import  url_for, request, abort, jsonify
from flask_login import login_user, current_user, logout_user, login_required, login_manager
from flaskblog.models import *
from sqlalchemy.exc import IntegrityError
import traceback
import json
from sqlalchemy import desc
import uuid
from uuid import UUID
from flask import Response
from flaskblog.routes import *


def populate_db_regions():
  db.create_all
  try:
      filename = os.path.join('./flaskblog/json/regions.json')
      with open(filename, encoding = 'utf-8') as regions_file:
          data = json.load(regions_file)
          if data:
            for region, val in data['regions'].items():
              main_region = Region(name=region, main_region=0)
              db.session.add(main_region)
              db.session.flush()
              for v in val:
                print(v)
                r = Region(name=v, main_region=main_region.id)
                db.session.add(r)
            db.session.commit()
            return
          else:
            print("data not found")    
  except IntegrityError:
    db.session.rollback()
    print('internal error') 
  except Exception as e:
      db.session.rollback()
      error = traceback.format_exc()
      print(error)
      return

def populate_db_products():
  try:
      filename = os.path.join('./flaskblog/json/products.json')
      with open(filename, encoding = 'utf-8') as products_file:
          data = json.load(products_file)
          if data:
            for product in data['products']:
              main_product = Product(product_name = product["product_name"], description = product["description_tm"], category_id = product["category_id"], brand_id = product["brand_id"], region_id = product["region_id"])
              db.session.add(main_product)
              db.session.flush() 
              sku_code = 'sku-'
              price = product["price"]
              quantity = product["quantity"]
              large_name=product["large_name"]
              small_name=product["small_name"]
              thumb_name=product["thumb_name"]
              sku_code = sku_code + str(time.time())
              sku_code = sku_code.replace(".", "")
              sku=Sku(product_id = main_product.id, sku = sku_code, price = price, quantity = quantity, large_name = large_name, small_name = small_name, thumb_name = thumb_name) 
              db.session.add(sku) 
              db.session.commit()
            print("success")
            return
          else:
              error = traceback.format_exc()
              print(error)
              print("data not found")    
  except IntegrityError:
    db.session.rollback()
    error = traceback.format_exc()
    print(error)
    print('internal error') 
  except Exception:
      db.session.rollback()
      error = traceback.format_exc()
      print(error)
      return      

def populate_db_categories():
  try:
      filename = os.path.join('./flaskblog/json/categories.json')
      with open(filename, encoding = 'utf-8') as categories_file:
          data = json.load(categories_file)
          if data:
            for category in data['categories']:
              main_category = Category( name = category["category_name_tm"], parent=category["parent_category"], image=category["category_image"], icon=category["category_icon"])
              db.session.add(main_category)
              db.session.commit()
              print("success")
            return
          else:
              print("data not found")    
  except IntegrityError:
    db.session.rollback()
    error = traceback.format_exc()
    print(error)
    print('internal error') 
  except Exception:
      db.session.rollback()
      error = traceback.format_exc()
      print(error)
      return 

def populate_db_brands():
  try:
      filename = os.path.join('./flaskblog/json/brand.json')
      with open(filename, encoding = 'utf-8') as brands_file:
          data = json.load(brands_file)
          if data:
            for brand in data['brands']:
              main_brand = Brand( brand_name=brand["brand_name"], brand_type=brand["brand_type"], brand_icon=brand["brand_icon"])
              db.session.add(main_brand)
              db.session.commit()
            print("success")
            return
          else:
              print("data not found")    
  except IntegrityError:
    db.session.rollback()
    error = traceback.format_exc()
    print(error)
    print('internal error') 
  except Exception:
      db.session.rollback()
      error = traceback.format_exc()
      print(error)
      return        

def populate_db_users():
  try:
      filename = os.path.join('./flaskblog/json/user.json')
      with open(filename, encoding = 'utf-8') as users_file:
          data = json.load(users_file)
          if data:
            for user in data['users']:
              user = Users(
                public_id = str(uuid.uuid4()),
                username = user['username'],
                email = user['email'],
                phone_number = user['phone'],
                role = user['role'], 
                region_id = user['region'], 
                parent = user['parent'],
                photo = user['photo'],
                password = bcrypt.generate_password_hash(user['password']).decode('utf-8')
              )
              # insert user
              db.session.add(user)
              db.session.commit()
            print("success")
            return
          else:
              print("data not found")    
  except IntegrityError:
    db.session.rollback()
    error = traceback.format_exc()
    print(error)
    print('internal error') 
  except Exception:
      db.session.rollback()
      error = traceback.format_exc()
      print(error)
      return         

def populate_db_cart():
  try:
      filename = os.path.join('./flaskblog/json/cart.json')
      with open(filename, encoding = 'utf-8') as cart_file:
          data = json.load(cart_file)
          if data:
            for cart in data['cart']:
              main_cart = Cart(user_id=cart["user_id"], sku_id=cart["sku_id"], quantity=cart["quantity"])
              db.session.add(main_cart)
              db.session.commit()
            print("success")
            return
          else:
              print("data not found")    
  except IntegrityError:
    db.session.rollback()
    error = traceback.format_exc()
    print(error)
    print('internal error') 
  except Exception:
      db.session.rollback()
      error = traceback.format_exc()
      print(error)
      return        

    


# Uncomment needed function. Populate of products must complete as last. 

# populate_db_regions()
# populate_db_users()
# populate_db_categories()
# populate_db_brands()
# populate_db_products()
# populate_db_cart()