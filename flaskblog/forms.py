from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField, SelectField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flaskblog import images
from flaskblog.models import Users
from datetime import datetime
from wtforms import MultipleFileField

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField ('Login')

class ProductForm(FlaskForm):
    product_name = StringField('Product', validators=[DataRequired()])
    description_tm = TextAreaField('Description in TM', validators=[DataRequired()])
    description_ru = TextAreaField('Description in RU', validators=[DataRequired()])
    picture = MultipleFileField('Product Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'])])
    price = FloatField('Price of product', validators=[DataRequired()])
    quantity = IntegerField('Quantity of product', validators=[DataRequired()])
    language = SelectField(u'Language', choices=[('tm','Turkmen'),('ru','Russian'),('en','English')])
    # category = SelectField(u'Category', choices=[('1','Clothes'),('2','T-Shirt'),('3','Shoes')])
    submit = SubmitField('Post')


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create User')

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

class SearchForm(FlaskForm):
    author = StringField('Author', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    created_at = StringField('Created Date', validators=[DataRequired()])
    
