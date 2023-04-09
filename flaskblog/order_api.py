
from flask import Blueprint
from sqlalchemy.sql.expression import null
from flaskblog import app, db
from flask import  url_for, request, abort, jsonify
from flask_login import login_user, current_user, logout_user, login_required, login_manager
from flaskblog.models import Product, Users, Category, Region, OrderItem, Orders
from sqlalchemy.exc import IntegrityError
import traceback
import json
from sqlalchemy import desc
import uuid
import random
from uuid import UUID
from flask import Response
from flaskblog.routes import *
from flaskblog.helper import *
from flask_cors import CORS, cross_origin

order_api = Blueprint('order_api', __name__,)
order_status = ['Order Recieved', 'Open', 'Partially Shipped', 'Shipped', 'Electronically Delivered', 'Completed', 'Cancelled', 'Action Required']

@order_api.route("/api/v1/orders", methods=['GET'])
@cross_origin(origin='localhost:8080',headers=['Content- Type','Authorization'])
@token_required
def api_orders(user):
    try:
        phone              = request.form.get('phone_number')
        address              = request.form.get('order_address')
        comment              = request.form.get('order_comment')
        print(user)
        if user.role == UserRole.SUPERADMIN:
            order_query = db.session.query(Orders, Users).join(Users, Orders.user_id == Users.id).order_by(Users.id, Orders.create_ts.desc()).all()
        elif user.role == UserRole.ADMIN :
            order_query = db.session.query(Orders, Users).join(Users, Orders.user_id == Users.id).filter(
                ((Users.id == user.id) | (Users.parent == str(user.id)))).order_by(Users.id, Orders.create_ts.desc()).all()
        else:
            order_query = db.session.query(Orders, Users).join(Users, Orders.user_id == Users.id).filter(
                Users.id == user.id).order_by(Users.id, Orders.create_ts.desc()).all()  
        orders = []
        for i in order_query:
            i_dict = {}
            i_dict["id"] = i[0].id
            i_dict["status"] = i[0].status
            i_dict["phone"] = i[0].phone
            i_dict["address"] = i[0].address
            i_dict["comment"] = i[0].comment
            i_dict["notes"] = i[0].notes
            i_dict["username"] = i[1].username
            i_dict["created_ts"] = i[0].create_ts.strftime("%Y-%m-%d %H:%M:%S")
            items = []
            totalSumList = []
            totalSum = null
            order_items = db.session.query(OrderItem, Sku).join(Sku, OrderItem.product_id == Sku.id).filter(OrderItem.order_id==i[0].id).order_by(OrderItem.id.desc()).all()
            for i in order_items:
                item_dict = {}
                item_dict["item_id"] = i[0].id
                item_dict["sku_id"] = i[0].product_id
                item_dict["codename"] = i[1].sku
                item_dict["quantity"] = i[0].quantity
                item_dict["price"] = i[0].price
                item_dict["sub_total"] = (i[0].price * i[0].quantity)
                item_dict["product_image"] = i[1].small_name
                items.append(item_dict)
                totalSumList.append(i[0].price * i[0].quantity)
                totalSum = sum(totalSumList)
            i_dict["order_items"] = items
            i_dict["total_sum"] = totalSum
            orders.append(i_dict)
        return Response(json.dumps(orders, cls=UUIDEncoder), mimetype="application/json") 
    except Exception as e:
            app.logger.info('api_order error: %s', str(e)) 
            error = traceback.format_exc()
            print(error)
            return Response("bad request", mimetype="application/json", status=400)            


@order_api.route("/api/v1/orders-info", methods=['GET'])
@cross_origin(origin='localhost:8080',headers=['Content- Type','Authorization'])
@token_required
def api_orders_info(user):
    try:
        if user.role == UserRole.SUPERADMIN:
            order_query = db.session.query(Orders, Users).join(Users, Orders.user_id == Users.id).order_by(Users.id, Orders.create_ts.desc()).all()
        elif user.role == UserRole.ADMIN :
            order_query = db.session.query(Orders, Users).join(Users, Orders.user_id == Users.id).filter(
                ((Users.id == user.id) | (Users.parent == str(user.id)))).order_by(Users.id, Orders.create_ts.desc()).all()
        orders = []
        orderTotalSumList = []
        productTotalCountList = []
        orderTotalSum = null
        orderTotalCount = len(order_query)
        productTotalCount = null
        recievedOrderTotalCount = 0
        completedOrderTotalCount = 0
        for i in order_query:
            i_dict = {}
            if i[0].status == 'Order Recieved':
                recievedOrderTotalCount += 1
            elif i[0].status == 'Completed':
                completedOrderTotalCount += 1    
            totalSumList = []
            totalSum = null
            order_items = db.session.query(OrderItem, Sku).join(Sku, OrderItem.product_id == Sku.id).filter(OrderItem.order_id==i[0].id).order_by(OrderItem.id.desc()).all()
            for i in order_items:
                totalSumList.append(i[0].price * i[0].quantity)
                totalSum = sum(totalSumList)
            orderTotalSumList.append(totalSum)
            productTotalCountList.append(len(order_items))
            productTotalCount = sum(productTotalCountList)
            orderTotalSum = sum(orderTotalSumList)
            print(orderTotalSumList)
            print(orderTotalSum) 
            print(recievedOrderTotalCount)   
            print(completedOrderTotalCount)
        i_dict["order_total_sum"] = orderTotalSum
        i_dict["order_total_count"] = orderTotalCount
        i_dict["product_total_count"] = productTotalCount
        i_dict["recieved_order_total_count"] = recievedOrderTotalCount
        i_dict["completed_order_total_count"] = completedOrderTotalCount
        orders.append(i_dict)
        return Response(json.dumps(i_dict), mimetype="application/json") 
    except Exception as e:
            app.logger.info('api_order error: %s', str(e)) 
            error = traceback.format_exc()
            print(error)
            return Response("bad request", mimetype="application/json", status=400) 

@order_api.route("/api/v1/order", methods=['POST'])
@cross_origin(origin='localhost:8080',headers=['Content- Type','Authorization'])
@token_required
def api_order_new(user):
    print(request.form)
    try:
        phone              = request.form.get('order_phone')
        address              = request.form.get('order_address')
        comment              = request.form.get('order_comment')
        order = Orders(user_id=user.id, phone=phone, address=address, comment=comment)
        db.session.add(order)
        db.session.flush()
        cart = Cart.query.with_entities(Cart.sku_id, Cart.quantity).filter(Cart.user_id == user.id)
        for item in cart:
            sku = Sku.query.filter_by(id = item.sku_id).first()
            order_item = OrderItem( order_id=order.id, quantity=item.quantity, price=sku.price, product_id=item.sku_id)
            db.session.add(order_item)
            product_quantity_sum = sku.quantity - item.quantity
            sku.quantity = product_quantity_sum
        db.session.query(Cart).filter(Cart.user_id == user.id).delete()
        db.session.commit()  
        app.logger.info('%s  accepted order number:  %s',
                    user.username, order.id)  
        return jsonify({ 'data': 'success'})
    except Exception as e:
            app.logger.info('api_order_new error: %s', str(e)) 
            error = traceback.format_exc()
            print(error)
            return Response("bad request", mimetype="application/json", status=400)       

@order_api.route("/api/v1/order/<string:uuid>", methods=['PUT'])
@cross_origin(origin='localhost:8080',headers=['Content- Type','Authorization'])
@token_required
def api_order_status(user, uuid):
    print(request.form)            
    try:
        if user.role == UserRole.SUPERADMIN or user.role == UserRole.ADMIN:
            print(uuid)
            order = Orders.query.filter(Orders.id==uuid).first()
            if request.form.get('order_status') in order_status:
                order.status = request.form.get('order_status')
                db.session.commit()
                return Response("success", mimetype="application/json") 
            else:
                app.logger.info('Value not exist')
                return Response("bad request", mimetype="application/json", status=400)
        else:
            app.logger.info('User role error')
            return Response("bad request", mimetype="application/json", status=400)             
    except Exception as e:
        app.logger.info('api_order_new error: %s', str(e)) 
        error = traceback.format_exc()
        print(error)
        return Response("bad request", mimetype="application/json", status=400)   