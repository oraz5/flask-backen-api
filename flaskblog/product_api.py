from flask import Blueprint
from flask import  request, jsonify
from flask import Response
from flaskblog import app, db
from flaskblog.routes import *
from flaskblog.helper import *
from flaskblog.models import Product, Users, Category, Region
from flask_login import login_user, current_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
from uuid import UUID
import traceback
import json
import time
from flask_cors import CORS, cross_origin

product_api = Blueprint('product_api', __name__,)

@product_api.route("/api/v1/product", methods=['POST'])
@cross_origin(origin='localhost:8080',headers=['Content- Type','Authorization'])
@token_required
def api_post_new(user):
    if request.method == 'POST':
        if user.role == UserRole.SUPERADMIN:
            try:
              sku_id = None
              picture_files = request.files.getlist('image_file')
              optionsArray = request.form.to_dict()
              print(request.form)
              print(type(optionsArray))
              print(optionsArray)
              print(type(picture_files))
              print(str(picture_files), type(picture_files))
              if picture_files:
                path_l="/static/product_photo" + time.strftime("/%Y/%m/%d/") 
                paht_s="/static/product_photo_small" + time.strftime("/%Y/%m/%d/") 
                picture_file_list = []
                for picture_file in picture_files:
                    picture_file = save_picture(picture_file, path_l)
                    picture_file_list.append(path_l + picture_file)
                small_image = save_picture_small(picture_files[0], paht_s)
                product_image = (paht_s + small_image)   
                product_name = request.form.get('product_name')
                description_tm = request.form.get('description_tm')
                description_ru = request.form.get('description_ru')
                description_en = request.form.get('description_en')
                language = request.form.get('language')
                category_id = request.form.get('category_id')
                region_id = request.form.get('region_id')
                brand_id = request.form.get('brand_id')
                product = Product(product_name = product_name, description_tm = description_tm, description_ru = description_ru, author = user,  
                          category_id = category_id, region_id = region_id, brand_id = brand_id )
                db.session.add(product)
                db.session.flush() 
                sku_code = 'sku-'
                sku_code_req = request.form.get('codename')
                price = request.form.get('price')
                quantity = request.form.get('quantity')
                sku_code = sku_code + str(time.time())
                sku_code = sku_code.replace(".", "")
                if sku_code_req:
                  sku_code = sku_code_req
                sku=Sku(product_id = product.id, sku = sku_code, price = price, quantity = quantity, large_name = picture_file_list, small_name = product_image) 
                db.session.add(sku) 
                db.session.flush() 
                category_query = Category.query.with_entities(Category.category_options).filter(Category.id == category_id).first()
                category_options= category_query[0]
                for k,v in optionsArray.items():
                  if k in category_options:
                    # print(k)
                    # print(v)
                    option = Option(product_id=product.id, name=k)
                    db.session.add(option)
                    db.session.flush()
                    # print("option_id: "+str(option.id))
                    option_value = OptionValue(product_id=product.id, option_id=option.id, name=v)
                    db.session.add(option_value)
                    db.session.flush()
                    sku_value=SkuValue(product_id=product.id, sku_id=sku.id, option_id=option.id, option_value_id=option_value.id )
                    db.session.add(sku_value)
                db.session.commit()  
                app.logger.info('%s  create successfully product:  %s',
                                user.username, product.id)
                return jsonify({ 'data': 'success'})
              else:
                return Response("bad request", mimetype="application/json", status=400)
            except IntegrityError as integrity:
                app.logger.info('New Product integrity error: %s', str(integrity)) 
                error = traceback.format_exc()
                print(error)
                db.session.rollback()
                return Response("bad request", mimetype="application/json", status=400) 
            except UnidentifiedImageError as undefined:
                app.logger.info('Product image error: %s', str(undefined)) 
                return Response("bad request", mimetype="application/json", status=400) 
            except json.decoder.JSONDecodeError as jsonError:
                app.logger.info('Json data insert error: %s', str(jsonError)) 
                return Response("bad request", mimetype="application/json", status=400) 
            except Exception as e:
                app.logger.info('New Product error: %s', str(e)) 
                error = traceback.format_exc()
                print(error)
                return Response("bad request", mimetype="application/json", status=400)
        else:
            return Response("bad request", mimetype="application/json", status=400)     
    return Response(json.dumps("no data"), mimetype="application/json")    


@product_api.route("/api/v1/product/variant/<int:product_id>", methods=['POST'])
@token_required
def api_post_add_variant(user, product_id):
    if request.method == 'POST':
        if user.role == UserRole.SUPERADMIN:
            try:
              sku_id = None
              picture_files = request.files.getlist('image_file')
              print(picture_files)
              optionsArray = request.form
              print(type(optionsArray))
              print(optionsArray)
              if picture_files:
                path_l="/static/product_photo" + time.strftime("/%Y/%m/%d/")
                paht_s="/static/product_photo_small" + time.strftime("/%Y/%m/%d/")
                picture_file_list = []
                for picture_file in picture_files:
                    picture_file = save_picture(picture_file, path_l)
                    picture_file_list.append(path_l + picture_file)
                small_image = save_picture_small(picture_files[0], paht_s)
                product_image = (paht_s + small_image) 
                sku_code = 'sku-'
                sku_code_req = request.form.get('sku_code')
                price = request.form.get('price')
                quantity = request.form.get('quantity')
                sku_code = sku_code + str(time.time())
                sku_code = sku_code.replace(".", "")
                if sku_code_req:
                  sku_code = sku_code_req
                sku=Sku(product_id = product_id, sku=sku_code, price=price, quantity=quantity, large_name = picture_file_list, small_name = product_image) 
                db.session.add(sku) 
                db.session.flush() 
                print("product_id: "+str(product_id) + " sku_id: "+str(sku.id))
                for k,v in optionsArray.items():
                  if [k] != ['product_name'] and [k] != ['description_tm'] and [k] != ['description_ru'] and [k] != ['description_en'] and [k] != ['language'] and [k] != ['category_id']  and [k] != ['region_id'] and [k] != ['brand_id'] and [k] != ['codename'] and [k] != ['quantity'] and [k] != ['price'] and [k] != ['image_file']:
                    print(k)
                    option = Option(product_id=product_id, name=k)
                    db.session.add(option)
                    db.session.flush()
                    option_value = OptionValue(product_id=product_id, option_id=option.id, name=v)
                    db.session.add(option_value)
                    db.session.flush()
                    sku_value=SkuValue(product_id=product_id, sku_id=sku.id, option_id=option.id, option_value_id=option_value.id )
                    db.session.add(sku_value)
                db.session.commit()  
                app.logger.info('%s  create successfully product variant:  %s',
                                user.username, product_id)
                return jsonify({ 'data': 'success'})
              else:
                print('error')
                return Response("bad request", mimetype="application/json", status=400)
            except IntegrityError as integrity:
                app.logger.info('New Product integrity error: %s', str(integrity)) 
                error = traceback.format_exc()
                print(error)
                db.session.rollback()
                return Response("bad request", mimetype="application/json", status=400) 
            except UnidentifiedImageError as undefined:
                app.logger.info('Product image error: %s', str(undefined)) 
                return Response("bad request", mimetype="application/json", status=400) 
            except json.decoder.JSONDecodeError as jsonError:
                app.logger.info('Json data insert error: %s', str(jsonError)) 
                return Response("bad request", mimetype="application/json", status=400) 
            except Exception as e:
                app.logger.info('New Product error: %s', str(e)) 
                error = traceback.format_exc()
                print(error)
                return Response("bad request", mimetype="application/json", status=400)
        else:
            return Response("bad request", mimetype="application/json", status=400)     
    return Response(json.dumps("no data"), mimetype="application/json")    

 
 

@product_api.route('/api/v1/products', methods=['GET'])
def api_all():
    search = request.args.get('search', default="", type=str)
    print(search)
    category_id = request.args.get('category_id', default=0, type=int)
    limit = request.args.get('limit', default=0, type=int)
    offset = request.args.get('offset', default=0, type=int)
    result_response = {}
    postCount = Product.query.filter(Product.active == True)
    sku_products = db.session.query(Sku, Product).join(Product, Sku.product_id==Product.id)
    # posts = db.session.query(Product, Category).join(Category, Product.category_id == Category.id).filter(Product.active == True, db.func.lower(Product.product_name).like('%' + search + '%'))
    if category_id > 0:
      print("cat>0")
      postCount = postCount.filter(Product.active == True, Product.category_id == category_id, db.func.lower(Product.product_name).like('%' + search + '%'))
      sku_products = sku_products.filter(Product.category_id == category_id)
    postCount = postCount.all()
    try:
      if limit:
        if offset:
          sku_products = sku_products.limit(limit).offset(offset).all()
        else:
          sku_products = sku_products.limit(limit).all()
      else:
        if offset:
            sku_products = sku_products.offset(offset).all()
        else:
            sku_products = sku_products.all()
      products = []
      if sku_products:
        result_response["total_count"] = len(postCount)
        for i in sku_products:
          i_dict = {}
          # print(i[0].id)
          i_dict["product_name"] = i[1].product_name
          i_dict["description_tm"] = i[1].description_tm
          i_dict["description_ru"] = i[1].description_ru
          i_dict["create_ts"] = i[1].create_ts
          i_dict["author"] = i[1].author.username
          i_dict["category_id"] = i[1].category_id
          # i_dict["category_name_tm"] = i[1].category_name_tm
          # i_dict["category_name_ru"] =  i[1].category_name_ru
          i_dict["create_ts"] = i_dict["create_ts"].strftime("%Y-%m-%d %H:%M:%S")
          # -----variatnts------
          i_dict["sku_id"] = i[0].id
          i_dict["sku_code"] = i[0].sku
          i_dict["sku_price"] = i[0].price
          i_dict["sku_quantity"] = i[0].quantity
          i_dict["sku_image"] = i[0].small_name
          options = []
          sku_values = SkuValue.query.filter(SkuValue.sku_id == i[0].id).all()
          # print(sku_values)
          sku_dict = {}
          if sku_values:
                for j in sku_values:
                  # print('id: '+str(j.id))
                  option_name = db.session.query(Option).filter(Option.id == j.option_id).first()
                  option_value = db.session.query(OptionValue).filter(OptionValue.id == j.option_value_id).first()
                  sku_dict[option_name.name] = option_value.name
          # print(sku_dict)
          options.append(sku_dict)
          i_dict["options"]=options
          products.append(i_dict)
        result_response["products"] = products
      return Response(json.dumps(result_response), mimetype="application/json")
    except Exception as e:
        app.logger.info(str(e))
        error = traceback.format_exc()
        print(error)
        return Response("internal error", mimetype="application/json", status=500)

#admin products shows products including variant 

@product_api.route('/api/v1/admin/products', methods=['GET'])
def api_all_admin():
    search = request.args.get('search', default="", type=str)
    print(search)
    category_id = request.args.get('category_id', default=0, type=int)
    limit = request.args.get('limit', default=0, type=int)
    offset = request.args.get('offset', default=0, type=int)
    result_response = {}
    postCount = Product.query.filter(Product.active == True)
    posts = db.session.query(Product).filter(Product.active == True, db.func.lower(Product.product_name).like('%' + search + '%'))
    if category_id > 0:
      postCount = postCount.filter(Product.active == True, Product.category_id == category_id, db.func.lower(Product.product_name).like('%' + search + '%'))
      posts = posts.filter(Product.category_id == category_id, Sku.active == True)
    postCount = postCount.all()
    try:
      if limit:
        if offset:
          posts = posts.limit(limit).offset(offset).all()
        else:
          posts = posts.limit(limit).all()
      else:
        if offset:
            posts = posts.offset(offset).all()
        else:
            posts = posts.all()
      products = []
      if posts:
        result_response["total_count"] = len(postCount)
        for i in posts:
          i_dict = {}
          i_dict["id"] = i.id
          i_dict["product_name"] = i.product_name
          i_dict["description_tm"] = i.description_tm
          i_dict["description_ru"] = i.description_ru
          i_dict["create_ts"] = i.create_ts
          i_dict["author"] = i.author.username
          i_dict["category_id"] = i.category_id
          i_dict["create_ts"] = i_dict["create_ts"].strftime("%Y-%m-%d %H:%M:%S")
          variants = []
          skus = db.session.query(SkuValue, Product).join(Product, SkuValue.product_id == Product.id).filter(SkuValue.product_id == i.id).order_by(SkuValue.id).all()
          if skus:
            sku_dict = {}
            for j in skus:
                product_sku = db.session.query(Sku).filter(Sku.id == j[0].sku_id).first()
                print(product_sku.sku)
                if product_sku.sku not in sku_dict:
                  skus_dict = {}
                  skus_dict["sku_id"] = j[0].sku_id
                  skus_dict["sku_code"] = product_sku.sku
                  skus_dict["price"] = product_sku.price
                  skus_dict["sku_image"] = product_sku.small_name
                  sku_dict[product_sku.sku] = skus_dict
                option_name = db.session.query(Option).filter(Option.id == j[0].option_id).first()
                option_value = db.session.query(OptionValue).filter(OptionValue.id == j[0].option_value_id).first()
                sku_dict[product_sku.sku][option_name.name] = option_value.name
            for k, v in sku_dict.items():
              variants.append(v)
            i_dict["variants"]=variants 
          products.append(i_dict)
        result_response["products"] = products
      return Response(json.dumps(result_response), mimetype="application/json")
    except Exception as e:
        app.logger.info(str(e))
        error = traceback.format_exc()
        print(error)
        return Response("internal error", mimetype="application/json", status=500)


@product_api.route("/api/v1/product/<string:sku_code>", methods=['GET'])
def api_single(sku_code):
    current_sku = Sku.query.filter_by(sku=sku_code, active=True).first()
    if current_sku: 
        i_dict = {}
        i_dict["sku_code"] = current_sku.sku
        i_dict["sku_price"] = current_sku.price
        i_dict["sku_quantity"] = current_sku.quantity
        i_dict["sku_images"] = current_sku.large_name
        sku_dict = {}
        sku_values = SkuValue.query.filter(SkuValue.sku_id == current_sku.id).all()
        if sku_values:
              for j in sku_values:
                option_name = db.session.query(Option).filter(Option.id == j.option_id).first()
                option_value = db.session.query(OptionValue).filter(OptionValue.id == j.option_value_id).first()
                sku_dict[option_name.name] = option_value.name
        i_dict["options"]=sku_dict        
        products = Product.query.filter_by(id=current_sku.product_id, state=True).first()
        if products:
                    products.count_viewed = products.count_viewed + 1
                    db.session.add(products)
                    db.session.commit()
                    i_dict["product_id"] = products.id
                    i_dict["product_name"] = products.product_name
                    i_dict["description_tm"] = products.description_tm
                    i_dict["description_ru"] = products.description_ru
                    i_dict["category_id"] = products.category_id
                    i_dict["create_ts"] = products.create_ts
                    i_dict["author"] = products.author.username
                    i_dict["language"] = products.language
                    i_dict["create_ts"] = i_dict["create_ts"].strftime("%Y-%m-%d %H:%M:%S")
                    i_dict["count_viewed"] = products.count_viewed
                    variants = []
                    skus = db.session.query(SkuValue, Product).join(Product, SkuValue.product_id == Product.id).filter(SkuValue.product_id == current_sku.product_id).order_by(SkuValue.id).all()
                    if skus:
                      sku_dict = {}
                      for i in skus:
                        if  current_sku.id!=i[0].sku_id:
                          product_sku = db.session.query(Sku).filter(Sku.id == i[0].sku_id).first()
                          print(product_sku.sku)
                          if product_sku.sku not in sku_dict:
                            skus_dict = {}
                            skus_dict["sku_id"] = i[0].sku_id
                            skus_dict["sku_codename"] = product_sku.sku
                            skus_dict["price"] = product_sku.price
                            sku_dict[product_sku.sku] = skus_dict
                          option_name = db.session.query(Option).filter(Option.id == i[0].option_id).first()
                          option_value = db.session.query(OptionValue).filter(OptionValue.id == i[0].option_value_id).first()
                          sku_dict[product_sku.sku][option_name.name] = option_value.name
                      for k, v in sku_dict.items():
                        variants.append(v)
                      i_dict["variants"]=variants  
                    result = i_dict
        return Response(json.dumps(result), mimetype="application/json")          
    else:
            result = {}
            result["error_code"] = 404
            result["error_code"] = "Not found"
            return Response(json.dumps(result), mimetype="application/json", status=404)

@product_api.route("/api/v1/product/<int:product_id>", methods=['DELETE'])
@token_required
def api_delete_product(user, product_id):
    try:
        if user.role == UserRole.SUPERADMIN:  
            if product_id:
                product = Product.query.get_or_404(product_id)
                product.active = False
                db.session.commit()
                app.logger.info('%s  delete successfully product with id: %s and name:  %s',
                                user.username, product.id, product.product_name)
                return Response("success", mimetype="application/json")
            else:
                app.logger.info('Product not found: %s', product_id)        
                return Response("Not found", mimetype="application/json", status=404)   
        else:
              return Response("bad request", mimetype="application/json", status=400)    
    except Exception as e:
          app.logger.info('api_removeFromCart error: %s', str(e)) 
          error = traceback.format_exc()
          print(error)
          return Response("bad request", mimetype="application/json", status=400) 

@product_api.route("/api/v1/processors", methods=['GET'])
def api_processors():
    if request.method == 'GET':
        json_file = open(app.root_path + '/json/processors.json')
        processors = json.load(json_file)
    return Response(json.dumps(processors), mimetype="application/json")           