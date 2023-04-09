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

region_api = Blueprint('region_api', __name__,)


@region_api.route("/api/v1/regions", methods=['GET'])
def api_region():
    print("region")
    if request.method == 'GET':
        regions = Region.query.filter(Region.active == True).order_by(desc(Region.id)).all()
        region=["regions"]
        if regions:
            for i in regions:
                i_dict = {}
                i_dict["id"] = i.id
                i_dict["name"] = i.name
                i_dict["main_region"] = i.main_region
                region.append(i_dict)  
    return Response(json.dumps(region), mimetype="application/json") 


    
@region_api.route("/api/v1/region", methods=['POST'])
@token_required
def api_region_new(user):
    if request.method == 'POST':
        name  = request.form.get('region_name')
        main_region_id  = request.form.get('main_region_id')
        if user.role == UserRole.SUPERADMIN:
            try:
                if name == None or main_region_id==None or name==""  or main_region_id=="":
                    return Response("bad request", mimetype="application/json", status=400)   
                else:
                    region = Region(name = name, main_region = main_region_id)
                    db.session.add(region)
                    db.session.commit()
                    app.logger.info('%s  create successfully region:  %s',
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


@region_api.route("/api/v1/region/<int:region_id>", methods=['GET'])
def api_region_id(region_id):
    print(region_id)  


@region_api.route("/api/v1/region/<int:region_id>", methods=['DELETE'])
@token_required
def api_region_delete(user, region_id):
    try:
        if user.role == UserRole.SUPERADMIN:
            region = Region.query.filter_by(id=region_id).first()
            if region_id is not None:
                region.active = False
                db.session.commit()
                app.logger.info('%s  deleted from region id:  %s and name: %s',
                        user.username, region.id, region.name)  
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