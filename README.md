# Flask Ecommerce web-backend
Hi this is porject for ecommerce backend and Adminstrative panel of ecommerce owner.
And here is API for this ecommerce. Below you can find instruction and endpoints for this project.

Instruction of Adminstrative website:

**1) Install all requirements  for python from file requirements.txt:**

>`python pip install -r requirements.txt`

**2) Create database in postgresql. Name of database which you added must be initialized in `__init__.py` :**

>`app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://{{db_user}}:{{passw}}@{{host}}/{{db_name}}"`

**3) The're three type of users Superadmin, Admin and simple User. The're have hierarchical relationship. Create Superadmin with Full priviligies.First need to run project. Then go to path:**

>`{{host}}:{{port}}/create_user`

write name of Superadmin, password and select Superadmin in Role

![Image of create_user](https://github.com/Oraz55/flask-backend/blob/master/create_user.png)

**4)(Optional) Use populate script populate_db.py and populate database with already exist data in static/json/ folder:**

>`python populate_db.py`


### Categories API

To create new category. Method type **POST**:

>`http://{{host}}:{{port}}/api/v1/category/new`

Form fields:
field | #description | #default value | #type |
--- | --- | --- | --- |
category_name_tm | Category name in TM language | --- | string
category_name_ru | Category name in RU language | --- | string
parent_category  | choose parent category       | 0(root)| int
image_file       | image file for category      | --- | string

To get all categories. Method type **GET**:

>`http://{{host}}:{{port}}/api/v1/category/all`

To get or delete category with id. Method type **GET, DELETE**:

>`http://{{host}}:{{port}}//api/v1/category/<int:category_id>`


### Product API

To create new product. Method type **POST**:

>`http://{{host}}:{{port}}/api/v1/product/new`

Form fields:
field | #description | #default value | #type |
--- | --- | --- | --- |
product_name | Product name | --- | string
description_tm | Product description in TM language | --- | text
description_ru  | Product description in RU language | ---| text
category_id       | category id of product | --- | int
brand_id       | category id of product | --- | int
region_id       | region id of product | --- | int
large_name  | list of image file | --- | string
language | language of product | --- |string
state | state of product | True | boolean
quantity | product quantity | 0 | int
price | product price | 0 | int
date_posted | product posted date | current time | datetime "/%Y/%m/%d/"

To get or delete single product. Method type **GET** , **DELETE**:

>`http://{{host}}:{{port}}/api/v1/product/<int:product_id>`

To get ALL product with category: Paginate with limit and offset. Method type **GET**

Param fields:
field | #description | #default value | #type |
--- | --- | --- | --- |
limit | limitation of product count | 0 | int
offset | start from index | 0 | int
category | products category | 0 | int

### Cart API

To add and delete single product in cart: Method type **POST**, **DELETE**

>`http://{{host}}:{{port}}/api/v1/product/cart/<int:product_id>`

Param fields:
field | #description | #default value | #type |
--- | --- | --- | --- |
quantity | quantity of porduct | --- | str


To get all products from current users cart: Method type **GET**

>`http://{{host}}:{{port}}/api/v1/cart`

### Order API

To get all orders of current user. Have hierarchical relationship. Method type **GET**

>`http://{{host}}:{{port}}/api/v1/orders`

To create orders from all products in users cart:  Method type **POST**

>`http://{{host}}:{{port}}/api/v1/new-cart`

