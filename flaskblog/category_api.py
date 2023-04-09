from flask import Blueprint
from flask import Response
from sqlalchemy.sql.elements import Null
from sqlalchemy.sql.expression import null
from flaskblog import app, db
from flaskblog.routes import *
from flaskblog.models import Category, Users
from flaskblog.helper import *
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy.exc import IntegrityError
import json
import traceback
from flask_cors import CORS, cross_origin

category_api = Blueprint('category_api', __name__,)

@category_api.route("/api/v1/category", methods=['POST'])
@token_required
def api_category_new(user):
    if request.method == 'POST':
        print(request.form)
        if user.role == UserRole.SUPERADMIN:
            try:
                    if request.files['image_file']:
                        path='static/cat_image/'
                        category_image = save_picture(request.files['image_file'], path)
                        print(category_image)
                        category_image = path + category_image
                        category_icon = save_picture_small(request.files['image_file'], path)
                        category_icon = path + category_icon
                        category_name_tm  = request.form.get('category_name_tm')
                        category_name_ru  = request.form.get('category_name_ru')
                        parent_category_id  = request.form.get('parent_category_id')
                        category = Category(category_name_tm = category_name_tm, category_name_ru = category_name_ru, category_image = category_image, parent_category = parent_category_id, category_icon = category_icon)
                        db.session.add(category)
                        db.session.commit()
                        print('sucess')
                        app.logger.info('%s  create successfully category:  %s',
                                    user.username, category_name_tm)
                        return jsonify({ 'data': 'success'})
                    else:
                        return Response("bad request", mimetype="application/json", status=400)
            except IntegrityError as integrity:
                app.logger.info('api_category_new error: %s', str(integrity)) 
                db.session.rollback()
                return Response("bad request", mimetype="application/json", status=400)
            except UnidentifiedImageError as undefined:
                app.logger.info('api_category_new error: %s', str(undefined)) 
                return jsonify({ 'data': 'image_error'})  
            except Exception as e:
                app.logger.info('api_category_new error: %s', str(e)) 
                error = traceback.format_exc()
                print(error)
                return Response("bad request", mimetype="application/json", status=400)
        else:
                return Response("bad request", mimetype="application/json", status=400)       


@category_api.route("/api/v1/category/<int:category_id>", methods=['PUT'])
@token_required
def api_category_edit(user, category_id):
    if request.method == 'PUT':
        print(request.form)
        if user.role == UserRole.SUPERADMIN:
            try:    
                    category = Category.query.filter_by(id = category_id, active = True).first()
                    if request.files.getlist('image_file'):
                        path='/static/cat_image/'
                        category_image = save_picture(request.files['image_file'], path)
                        print(category_image)
                        category.category_image = path + category_image
                        category_icon = save_picture_small(request.files['image_file'], path)
                        category.category_icon = path + category_icon
                    if request.form.get('category_name_tm') !='' or request.form.get('category_name_tm') !=null:   
                        category.category_name_tm  = request.form.get('category_name_tm')
                    if request.form.get('category_name_ru') !='' or request.form.get('category_name_ru') !=null:    
                        category.category_name_ru  = request.form.get('category_name_ru')
                    if request.form.get('parent_category_id') !='' or request.form.get('parent_category_id') !=null:    
                        category.parent_category_id  = request.form.get('parent_category_id')
                    category.version += 1
                    db.session.commit()
                    print('sucess')
                    app.logger.info('%s  create successfully category:  %s',
                                user.username, category.category_name_tm)
                    return jsonify({ 'data': 'success'})
            except IntegrityError as integrity:
                app.logger.info('api_category_new error: %s', str(integrity)) 
                db.session.rollback()
                error = traceback.format_exc()
                print(error)
                return Response("bad request", mimetype="application/json", status=400)
            except UnidentifiedImageError as undefined:
                app.logger.info('api_category_new error: %s', str(undefined)) 
                error = traceback.format_exc()
                print(error)
                return jsonify({ 'data': 'image_error'})  
            except Exception as e:
                app.logger.info('api_category_new error: %s', str(e)) 
                error = traceback.format_exc()
                print(error)
                return Response("bad request", mimetype="application/json", status=400)
        else:
                return Response("bad request", mimetype="application/json", status=400)       



@category_api.route("/api/v1/categories", methods=['GET'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def api_category():
    try:
        categories = Category.query.order_by(Category.id).filter_by(active = True).all()
        category = []
        if categories:
            for i in categories:
                i_dict = {}
                i_dict["id"] = i.id
                i_dict["category_name_tm"] = i.category_name_tm
                i_dict["category_name_ru"] = i.category_name_ru
                i_dict["parent_category"] = i.parent_category
                i_dict["category_image"] = i.category_image
                i_dict["category_icon"] = i.category_icon
                options= i.category_options
                optionsArray = []
                for j in options:
                    optionsArray.append(j) 
                i_dict["options"] = optionsArray  
                category.append(i_dict)
            return Response(json.dumps(category), mimetype="application/json")
    except Exception as e:
        app.logger.info('All Category error: %s', str(e)) 
        error = traceback.format_exc()
        print(error)  
        return Response("bad request", mimetype="application/json", status=400)

   

@category_api.route("/api/v1/category/<int:category_id>", methods=['GET'])
@cross_origin(origin='localhost:8080',headers=['Content- Type','Authorization'])
def api_category_id(category_id):
    print(category_id)  
    try:
        category = Category.query.filter_by(id=category_id).first()
        if category:
                i_dict = {}
                i_dict["id"] = category.id
                i_dict["category_name_tm"] = category.category_name_tm
                i_dict["category_name_ru"] = category.category_name_ru
                i_dict["parent_category"] = category.parent_category
                i_dict["category_image"] = category.category_image
                i_dict["category_icon"] = category.category_icon
                result = i_dict
                return Response(json.dumps(result), mimetype="application/json")
        else:
            app.logger.info('Category not found: %s', category_id)
            return Response("Not found", mimetype="application/json", status=404)
    except Exception as e:   
        app.logger.info('Category error: %s', str(e))         
        return Response("bad request", mimetype="application/json", status=400)

@category_api.route("/api/v1/category/<int:category_id>", methods=['DELETE'])
@token_required
def api_category_delete(user, category_id):
    if user.role == UserRole.SUPERADMIN:
        try:  
            if category_id:
                category = Category.query.get_or_404(category_id)
                category.active = False
                db.session.commit()
                app.logger.info('%s  deleted successfully category with id: %s and name:  %s',
                                user.username, category.id, category.name)
                return Response("success", mimetype="application/json")
            else:
                app.logger.info('Category not found: %s', category_id)        
                return Response("Not found", mimetype="application/json", status=404)    
        except Exception as e:
            app.logger.info('Category error: %s', str(e))         
            return Response("bad request", mimetype="application/json", status=400)    
    else:
        return Response("bad request", mimetype="application/json", status=400)             

@category_api.route("/api/v1/category/value/<int:category_id>", methods=['GET'])
@cross_origin(origin='localhost:8080',headers=['Content- Type','Authorization'])
def api_category_values(category_id):
    try:
        options = db.session.query(Option).join(Product).filter(Product.category_id==category_id, Product.active == True).all()
        category = Category.query.filter(Category.id==category_id).first()
        optionsCat= category.category_options
        result={}
        for i in options:
            if i.name not in result:
                result[i.name] = []
            option_value = db.session.query(Option, OptionValue).join(Option, OptionValue.option_id == Option.id).filter(OptionValue.option_id==i.id).all()
            for value in option_value:
                if value[1].name not in result[i.name]:
                    result[i.name].append(value[1].name)
        for k in optionsCat:
            if k not in result:
                result[k] = []            
        return Response(json.dumps(result), mimetype="application/json")
    except Exception as e:
            app.logger.info('Category error: %s', str(e)) 
            error = traceback.format_exc()
            print(error)        
            return Response("bad request", mimetype="application/json", status=400)   

@category_api.route("/api/v1/category/option/<int:category_id>", methods=['GET'])
@cross_origin(origin='localhost:8080',headers=['Content- Type','Authorization'])
def api_category_options(category_id):
    try:
        category = Category.query.filter(Category.id==category_id, Category.active == True).first()
        options= category.category_options
        result=[]
        for i in options:
            result.append(i)  
        return Response(json.dumps(result), mimetype="application/json")
    except Exception as e:
            app.logger.info('Category error: %s', str(e)) 
            error = traceback.format_exc()
            print(error)        
            return Response("bad request", mimetype="application/json", status=400)            

@category_api.route("/api/v1/category/option/<int:category_id>", methods=['POST'])
@cross_origin(origin='localhost:8080',headers=['Content- Type','Authorization'])
def api_category_add_options(category_id):
    try:
        options = request.get_json()
        print(request.data)
        category = Category.query.filter(Category.id==category_id, Category.active == True).first()
        exist_options = ''
        for i in options:
            print(i)
            print(category.category_options)
            if i not in category.category_options:
                category.category_options = category.category_options + [i]
                db.session.commit()
            else:
                if exist_options != '':
                    exist_options+=str(", " + i)
                else:
                    exist_options+=str(i)
        if exist_options != '':
            exist_options= ", but " + exist_options + str(' already exist')    
        return Response(json.dumps("success" + exist_options), mimetype="application/json")
    except Exception as e:
            app.logger.info('Category error: %s', str(e)) 
            error = traceback.format_exc()
            print(error)        
            return Response("bad request", mimetype="application/json", status=400)  

@category_api.route("/api/v1/category/option/<int:category_id>", methods=['DELETE'])
@cross_origin(origin='localhost:8080',headers=['Content- Type','Authorization'])
def api_category_remove_options(category_id):
    try:
        options = request.get_json()
        print(options)
        category = Category.query.filter(Category.id==category_id, Category.active == True).first()
        not_exist_options = ''
        new_list = []
        for category_option in category.category_options:
            new_list.append(category_option)
        for option in options:
            print(option)
            print(type(option))
            print(new_list)
            for category_option in new_list:
                if option == category_option:
                    new_list.remove(option)
                    break
                else:
                    if not_exist_options != '':
                        not_exist_options+=str(", " + option)
                    else:
                        not_exist_options+=str(option)
        if not_exist_options != '':
            not_exist_options= ", but " + not_exist_options + str(' not exist')
        print(new_list)
        category.category_options = new_list
        db.session.commit()
        return Response(json.dumps("success" + not_exist_options), mimetype="application/json")
    except Exception as e:
            app.logger.info('Category error: %s', str(e)) 
            error = traceback.format_exc()
            print(error)        
            return Response("bad request", mimetype="application/json", status=400)                    

