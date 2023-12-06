from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, EmailField, PasswordField, DateField, TelField,
                     BooleanField, IntegerField, FloatField, SelectField, DateTimeField, TimeField)
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import datetime as dt



class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    surname = StringField("Surname", validators=[DataRequired()])
    age = DateField('Age', validators=[DataRequired()])
    tel = TelField('Tell', validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Join Me")


class ProductPost(FlaskForm):
    name = SelectField("Name", validators=[DataRequired()], choices=[('', 'Select An Item'), ('Bear', 'Bear'), ('Cat', 'Cat')])
    img_url = StringField("Image URL", validators=[DataRequired()])
    in_sale = BooleanField("Sale")
    discount = IntegerField("Discount", default=0)
    price = FloatField("Price", validators=[DataRequired()])
    stock = IntegerField("Stock", validators=[DataRequired()])
    comment = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("OK")


class MakeCart(FlaskForm):
    quantity = IntegerField("Quantity", validators=[DataRequired()])
    submit = SubmitField("Purchase")



