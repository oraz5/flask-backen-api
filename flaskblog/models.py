from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin
from enum import Enum, unique
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKeyConstraint, UniqueConstraint
import uuid
from geoalchemy2 import Geometry


class UserRole(Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    USER = "user"


    @staticmethod
    def from_string(string):
        if string.lower() == "superadmin":
            return UserRole.SUPERADMIN
        elif string.lower() == "admin":
            return UserRole.ADMIN
        elif string.lower() == "user":
            return UserRole.USER
        else:
            return None

    def __str__(self):
        return '%s' % self.value

class StateT(Enum):
    enabled = "enabled"
    disabled = "disabled"
    deleted = "deleted"


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique = True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(70), unique = True)
    phone_number = db.Column(db.String(70), unique = True)
    address = db.Column(db.String(70), unique = False)
    photo = db.Column(db.String(70), unique = True)
    role = db.Column('role', db.Enum(UserRole), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey(
        'region.id'), nullable=True)
    parent = db.Column(db.Integer, unique=False, nullable=False)
    create_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    update_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    state = db.Column('state', db.Enum(StateT), nullable=False, default=StateT.enabled)
    version = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"User('{self.username}')"


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    parent = db.Column(db.Integer, nullable=False)
    product = db.relationship('Product', backref='category')
    image = db.Column(db.String(100), nullable=True)
    icon = db.Column(db.String(100), nullable=True)
    create_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    update_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    state = db.Column('state', db.Enum(StateT), nullable=False, default=StateT.enabled)
    version = db.Column(db.Integer, default=0)

class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand_name = db.Column(db.String(50), nullable=False)
    brand_type = db.Column(db.String(50), nullable=False)
    product = db.relationship('Product', backref='brand')
    brand_icon = db.Column(db.String(100), nullable=True)
    create_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    update_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    state = db.Column('state', db.Enum(StateT), nullable=False, default=StateT.enabled)
    version = db.Column(db.Integer, default=0)

class Product(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey(
        'category.id'), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey(
        'brand.id'), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey(
        'region.id'), nullable=False)    
    create_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    update_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    state = db.Column('state', db.Enum(StateT), nullable=False, default=StateT.enabled)
    version = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"Product('{self.product_name}', '{self.create_ts}')"


class Currency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, default=0)
    local_value = db.Column(db.Float, default=0)
    start_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_at = db.Column(db.DateTime, nullable=False)
    create_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    update_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    state = db.Column('state', db.Enum(StateT), nullable=False, default=StateT.enabled)
    version = db.Column(db.Integer, default=0)


class Discount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.BigInteger, db.ForeignKey(
        'product.id'), nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    percent = db.Column(db.Float, default=0)
    status = db.Column(db.Boolean, default=False, nullable=False)
    start_at = db.Column(db.DateTime, nullable=False)
    end_at = db.Column(db.DateTime, nullable=False)
    create_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    update_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    state = db.Column('state', db.Enum(StateT), nullable=False, default=StateT.enabled)
    version = db.Column(db.Integer, default=0)


class Cart(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), nullable=False, primary_key=True)
    sku_id = db.Column(db.BigInteger, db.ForeignKey(
        'sku.id'), nullable=False, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    create_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    update_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    state = db.Column('state', db.Enum(StateT), nullable=False, default=StateT.enabled)
    version = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"Cart('{self.user_id}', '{self.sku_id}, '{self.quantity}')"


class Orders(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    address = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(100), nullable=True)
    comment = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='Order Recieved', nullable=False)
    create_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    update_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    state = db.Column('state', db.Enum(StateT), nullable=False, default=StateT.enabled)
    version = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<orderID: {self.id}>'


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(UUID(as_uuid=True),
                         db.ForeignKey('orders.id'), nullable=False)
    sku_id = db.Column(db.BigInteger, db.ForeignKey(
        'sku.id'), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, default=0)
    create_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    update_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    state = db.Column('state', db.Enum(StateT), nullable=False, default=StateT.enabled)
    version = db.Column(db.Integer, default=0)


# class ProductCurrency(db.Model):
#     product_id = db.Column(db.BigInteger, db.ForeignKey(
#         'product.id'), nullable=False, primary_key=True)
#     currency_id = db.Column(db.Integer, db.ForeignKey(
#         'currency.id'), nullable=False)


# class ProductCategory(db.Model):
#     product_id = db.Column(db.BigInteger, db.ForeignKey(
#         'product.id'), nullable=False, primary_key=True)
#     category_id = db.Column(db.Integer, db.ForeignKey(
#         'category.id'), nullable=False)


class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    main_region = db.Column(db.Integer, nullable=False)
    #coordinates = db.Column(Geometry('POINT'))
    create_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    update_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    state = db.Column('state', db.Enum(StateT), nullable=False, default=StateT.enabled)
    version = db.Column(db.Integer, default=0)



# class Image(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     large_name = db.Column(db.String(100), nullable=True)
#     large_height = db.Column(db.Integer, nullable=False)
#     large_width = db.Column(db.Integer, nullable=False)
#     small_name = db.Column(db.String(100), nullable=True)
#     small_height = db.Column(db.Integer, nullable=False)
#     small_width = db.Column(db.Integer, nullable=False)
#     thumb_name = db.Column(db.String(100), nullable=True)
#     thumb_width = db.Column(db.Integer, nullable=False)
#     thumb_height = db.Column(db.Integer, nullable=False)
#     create_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
#     update_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
#     active = db.Column(db.Boolean, nullable=False, default=True)
#     version = db.Column(db.Integer, default=0)

class Option(db.Model):
    id = db.Column(db.BigInteger, nullable=False, primary_key=True)
    category_id = db.Column(db.BigInteger, db.ForeignKey(
        'category.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False, unique=True)
    create_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    update_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    state = db.Column('state', db.Enum(StateT), nullable=False, default=StateT.enabled)
    version = db.Column(db.Integer, default=0)
    # __table_args__ = (UniqueConstraint('product_id', 'name', name='_option_'),)

class OptionValue(db.Model):
    id = db.Column(db.BigInteger, nullable=False, primary_key=True)
    option_id = db.Column(db.BigInteger, db.ForeignKey(
        'option.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False, unique=True)
    create_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    update_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    state = db.Column('state', db.Enum(StateT), nullable=False, default=StateT.enabled)
    version = db.Column(db.Integer, default=0)    
    # __table_args__ = (
    #     ForeignKeyConstraint(
    #         ['product_id', 'id'],
    #         ['option.product_id', 'option.id']
    #     ),
    # )
    # __table_args__ = (UniqueConstraint('product_id', 'option_id', name='_value_'),)

class Sku(db.Model):
    id = db.Column(db.BigInteger, nullable=False, primary_key=True)
    product_id = db.Column(db.BigInteger, db.ForeignKey(
        'product.id'), nullable=False)
    sku = db.Column(db.String(30), nullable=False, unique=True)
    price = db.Column(db.Float, default=0)
    quantity = db.Column(db.Integer, default=0)
    large_name = db.Column(db.String(300), nullable=True)
    small_name = db.Column(db.String(100), nullable=True)
    thumb_name = db.Column(db.String(100), nullable=True)
    count_viewed = db.Column(db.Integer, default=0)
    create_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    update_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    state = db.Column('state', db.Enum(StateT), nullable=False, default=StateT.enabled)
    version = db.Column(db.Integer, default=0)   
    # __table_args__ = (UniqueConstraint('product_id', 'sku', name='_value_'),)  

class SkuValue(db.Model):
    id = db.Column(db.BigInteger, nullable=False, primary_key=True)
    sku_id = db.Column(db.Integer, db.ForeignKey(
        'sku.id'), nullable=False)
    option_id = db.Column(db.Integer, db.ForeignKey(
        'option.id'), nullable=False)
    option_value_id = db.Column(db.Integer, db.ForeignKey(
        'option_value.id'), nullable=False)
    create_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    update_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    state = db.Column('state', db.Enum(StateT), nullable=False, default=StateT.enabled)
    version = db.Column(db.Integer, default=0)    

db.create_all()
