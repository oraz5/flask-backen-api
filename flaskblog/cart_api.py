from flask import Blueprint
from flask import Response
from flask import  request, abort, jsonify
from flaskblog import app, db,  bcrypt
from flaskblog.routes import *
from flaskblog.helper import *
from flaskblog.models import Product, Users, Category, Cart
from flask_login import login_user, current_user, logout_user, login_required, login_manager
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
import traceback
import json
import uuid
from uuid import UUID
from flask_cors import CORS, cross_origin

cart_api = Blueprint('cart_api', __name__,)


@cart_api.route("/api/v1/cart", methods=['GET'])
@cross_origin(origin='localhost:8080',headers=['Content- Type','Authorization'])
@token_required
def api_cart(user):
    print(request.form)
    try:
        productsincart = Product.query.join(Sku, Product.id == Sku.product_id).join(Cart) \
            .add_columns(Sku.sku, Cart.quantity ,Sku.price, Sku.small_name).filter(Cart.user_id == user.id, Cart.active == True)
        products = []
        for i in productsincart:
            i_dict = {}
            i_dict["user_id"] = i[0].user_id
            i_dict["product_id"] = i[0].id
            i_dict["sku_code"] = i[1]
            i_dict["description_tm"] = i[0].description_tm
            i_dict["description_ru"] = i[0].description_ru
            i_dict["quantity"] = i[2]
            i_dict["price"] = i[3]
            i_dict["small_name"] = i[4]
            products.append(i_dict)
        return Response(json.dumps(products, cls=UUIDEncoder), mimetype="application/json") 
    except Exception as e:
            app.logger.info('api_add_cart error: %s', str(e)) 
            error = traceback.format_exc()
            print(error)
            return Response("bad request", mimetype="application/json", status=400)   


@cart_api.route("/api/v1/product/cart/<string:codename>", methods=['POST'])
@cross_origin(origin='localhost:8080',headers=['Content- Type','Authorization'])
@token_required
def api_add_cart(user, codename):
    try:
        print(request)
        quantity_str = request.form.get('quantity')
        quantity = int(quantity_str)
        # product = Product.query.get_or_404(product_id)
        sku = Sku.query.filter_by(sku=codename).first()
        print(quantity_str)
        print(user)
        cart = Cart.query.filter_by(user_id=user.id, sku_id=sku.id).first()
        if cart:
            cart.quantity = cart.quantity + quantity
        else:            
            new_cart = Cart(sku_id=sku.id, user_id=user.id, quantity=quantity)
            db.session.add(new_cart)
        db.session.commit()
        app.logger.info('%s  added to cart product with name: %s',
                    user.username, sku.sku)  
        return Response("success", mimetype="application/json")
    except ValueError as value:
            app.logger.info('api_add_cart value error: %s', str(value)) 
            db.session.rollback()
            return Response("quantity value error", mimetype="application/json", status=400)      
    except Exception as e:
            app.logger.info('api_add_cart error: %s', str(e)) 
            error = traceback.format_exc()
            print(error)
            return Response("bad request", mimetype="application/json", status=400)   

@cart_api.route("/api/v1/product/cart/<string:codename>", methods=['DELETE'])
@cross_origin(origin='localhost:8080',headers=['Content- Type','Authorization'])
@token_required
def api_sub_cart(user, codename):
    try:
        print(request)
        quantity_str = request.form.get('quantity')
        quantity = int(quantity_str)
        # product = Product.query.get_or_404(product_id)
        sku = Sku.query.filter_by(sku=codename).first()
        print(quantity_str)
        print(quantity)
        print(user)
        cart = Cart.query.filter_by(user_id=user.id, sku_id=sku.id).first()
        if cart and cart.quantity > 0:
            cart.quantity = cart.quantity - quantity
        db.session.commit()
        app.logger.info('%s  added to cart product with name: %s',
                    user.username, sku.sku)  
        return Response("success", mimetype="application/json")
    except ValueError as value:
            app.logger.info('api_add_cart value error: %s', str(value)) 
            db.session.rollback()
            return Response("quantity value error", mimetype="application/json", status=400)      
    except Exception as e:
            app.logger.info('api_add_cart error: %s', str(e)) 
            error = traceback.format_exc()
            print(error)
            return Response("bad request", mimetype="application/json", status=400)   
