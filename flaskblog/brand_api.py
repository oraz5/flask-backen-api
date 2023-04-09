import os
from flask import Blueprint
from flask import redirect, request, abort, jsonify
from flaskblog import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required, login_manager
from flaskblog.models import *
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
import json
import traceback
import logging
from flaskblog.helper import token_required
from flask import Response

brand_api = Blueprint('brand_api', __name__,)


@brand_api.route("/api/v1/brands", methods=['GET'])
def api_region():
    print("region")
    if request.method == 'GET':
        brands = Brand.query.filter(Brand.active == True).order_by(desc(Brand.id)).all()
        brandList = {}
        brand=[]
        if brands:
            for i in brands:
                i_dict = {}
                i_dict["id"] = i.id
                i_dict["name"] = i.brand_name
                i_dict["type"] = i.brand_type
                i_dict["icon"] = i.brand_icon
                brand.append(i_dict)  
            brandList["brands"] = brand    
    return Response(json.dumps(brandList), mimetype="application/json") 


    
@brand_api.route("/api/v1/brand", methods=['POST'])
@token_required
def api_brand_new(user):
    if request.method == 'POST':
        name  = request.form.get('name')
        brand_type  = request.form.get('brand_type')
        if user.role == UserRole.SUPERADMIN:
            try:
                if name == None or brand_type==None or name==""  or brand_type=="":
                    return Response("bad request", mimetype="application/json", status=400)   
                else:
                    brand = Brand(name = name, brand_type = brand_type)
                    db.session.add(brand)
                    db.session.commit()
                    app.logger.info('%s  create successfully brand:  %s',
                                user.username, name)
                    return Response("success", mimetype="application/json")   
            except IntegrityError as integrity:
                app.logger.info('api_region_new error: %s', str(integrity)) 
                db.session.rollback()
                return jsonify({ 'data': 'db_error'}) 
            except Exception as e:
                app.logger.info('api_region_new error: %s', str(e)) 
                error = traceback.format_exc()
                print(error)
                return Response("bad request", mimetype="application/json", status=400)
        else:
            return Response("bad request", mimetype="application/json", status=400) 


@brand_api.route("/api/v1/region/<int:brand_id>", methods=['POST'])
def api_brand_id(brand_id):
    print(brand_id)  


@brand_api.route("/api/v1/brand/<int:brand_id>", methods=['DELETE'])
@token_required
def api_brand_delete(user, brand_id):
    try:
        if user.role == UserRole.SUPERADMIN:
            brand = Region.query.filter_by(id=brand_id).first()
            if brand_id is not None:
                brand.active = False
                db.session.commit()
                app.logger.info('%s  deleted from brand id:  %s and name: %s',
                        user.username, brand.id, brand.name)  
                return Response("success", mimetype="application/json")
            else:
                return Response("error", mimetype="application/json", status=400)
        else:
            return Response("bad request", mimetype="application/json", status=400)
    except Exception as e:
            app.logger.info('api_removeFromCart error: %s', str(e)) 
            error = traceback.format_exc()
            print(error)
            return Response("bad request", mimetype="application/json", status=400)     