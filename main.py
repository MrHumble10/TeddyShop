from __future__ import print_function

import random
from itertools import product

from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from forms import ProductPost, RegisterForm, MakeCart, PassForgot
import datetime as dt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, current_user, logout_user
from functools import wraps
from flask_gravatar import Gravatar
import os
from notifications import send_email, send_code

today = dt.datetime.now()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lkbljhgcjgfnvbhnm'
# os.environ.get('SECRET_KEY')
Bootstrap5(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///posts.db")
db = SQLAlchemy()
db.init_app(app)

ckeditor = CKEditor(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    surname = db.Column(db.String(80), nullable=False)
    age = db.Column(db.String, nullable=False)
    tel = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    # cart_purchase = db.relationship("Cart", back_populates="customer")
    # comments = db.relationship("Comment", back_populates="author_comment")
    # products = db.relashenship('Product', back_populates="customer")


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    # customer = db.relationship('User', back_populates='products')
    # customer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(80), nullable=False)
    in_sale = db.Column(db.String(20), nullable=False)
    about = db.Column(db.String, nullable=False)
    discount = db.Column(db.Integer)
    price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    # product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product_img = db.Column(db.String, nullable=False)
    product_price = db.Column(db.Float, nullable=False)
    product_info = db.Column(db.String, nullable=False)
    product_total = db.Column(db.Float, nullable=False)
    customer_id = db.Column(db.Integer, nullable=False)
    # customer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created = db.Column(db.String, nullable=False)
    modified = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    # product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product_price = db.Column(db.Float, nullable=False)
    customer_id = db.Column(db.Integer, nullable=False)
    # customer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created = db.Column(db.String, nullable=False)


# CONFIGURE TABLE
# class BlogPost(db.Model):
#     __tablename__ = "blog_post"
#     id = db.Column(db.Integer, primary_key=True)
#     author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
#     author = db.relationship("User", back_populates="posts")
#     title = db.Column(db.String(250), unique=True, nullable=False)
#     subtitle = db.Column(db.String(250), nullable=False)
#     date = db.Column(db.String(250), nullable=False)
#     body = db.Column(db.Text, nullable=False)
#     img_url = db.Column(db.String(250), nullable=False)
#     comments = db.relationship("Comment", back_populates="post_comment")


with app.app_context():
    db.create_all()


# Create admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if not current_user.is_authenticated or current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash('You need to log out to access the register page')
        return redirect(url_for('home'))

    form = RegisterForm()
    psw_hashed_with_salt = generate_password_hash(f'{form.password.data}',
                                                  method='pbkdf2:sha256',
                                                  salt_length=8
                                                  )
    if form.validate_on_submit():
        new_user = User(
            name=form.name.data,
            surname=form.surname.data,
            age=form.age.data,
            tel=form.tel.data,
            email=form.email.data,
            password=psw_hashed_with_salt,
        )
        # if username is in DB so direct users in login page
        result = db.session.execute(db.Select(User).where(User.email == new_user.email))
        user = result.scalar()
        if user:
            flash(f"*{user.email}*")
            flash("already exist. Log In instead!")
            return redirect(url_for('login'))
        else:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home'))
    return render_template("register.html", form=form, item_num=item_num)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']
        result = db.session.execute(db.Select(User).where(User.email == email))
        user = result.scalar()
        if not user:
            flash("Email does not exist.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash("The password is wrong.")
            return redirect(url_for('login'))
        else:
            login_user(user)
        return redirect(url_for('home'))

    return render_template('login.html', logged_in=current_user.is_authenticated)


code = ""


def make_code():
    global code
    confirm_code = [random.randint(0, 9) for _ in range(0, 6)]
    code = 'TDS-' + "".join(str(x) for x in confirm_code)
    return code

PASS_CHANGE_EMAIL = ""
@app.route("/pass_forget", methods=["GET", "POST"])
def pass_forgot():
    global PASS_CHANGE_EMAIL

    if request.method == "POST":
        PASS_CHANGE_EMAIL = request.form['email']
        email = request.form['email']
        user = db.session.execute(db.Select(User).where(User.email == email)).scalar()
        if not user:
            flash("Sorry!, there is not such email!!!")

        else:
            make_code()
            send_code(username=f"{user.name} {user.surname}",
                      email=email,
                      msg=code)
            flash("A code has been sent to your email.")
            return redirect(url_for('pass_forgot'))
    return render_template("pass_forgot.html", item_num=item_num)


@app.route("/check_code", methods=["GET", "POST"])
def check_code():
    if request.method == "POST":
        if request.form["code"] != code:
            flash("Please enter the correct code.")
            return redirect(url_for('pass_forgot'))
        else:
            make_code()
            return redirect(url_for('change_pass'))


@app.route("/change_pass", methods=["GET", "POST"])
def change_pass():
    global PASS_CHANGE_EMAIL
    if request.method == "POST":
        new_password_hash = generate_password_hash(password=request.form['new_pass'],
                                                   method="pbkdf2:sha256",
                                                   salt_length=8)
        user = db.session.execute(db.Select(User).where(User.email == PASS_CHANGE_EMAIL)).scalar()
        print(user.name)
        if request.form['new_pass'] != request.form['cnf_pass']:
            flash("Sorry!, password is not configured try again!!!")
        else:
            user.password = new_password_hash
            db.session.commit()
            return render_template('login.html', logged_in=current_user.is_authenticated)

    return render_template("pass_forgot.html", item_num=item_num, change_pass=True)


def days_ago(from_str, to_str):
    date_from = dt.datetime.strptime(from_str, "%Y-%m-%d")
    date_to = dt.datetime.strptime(to_str, "%Y-%m-%d")
    days = (date_from - date_to).days

    # to get rid of " - " for example -25 days ago. It
    # has been simplified to * -1 to reach a positive number.
    return days * -1


item_num = 0


@app.route('/')
def home():
    result = db.session.execute(db.select(Product))
    product = result.scalars().all()
    result = db.session.execute(db.Select(Cart))
    cart_items = result.scalars().all()
    result = db.session.execute(db.Select(Favorite))
    fav_items = result.scalars().all()
    global item_num
    item_num = 0
    for item in cart_items:
        if current_user.is_authenticated and item.customer_id == current_user.id:
            item_num += item.quantity
        if days_ago(item.created, today.strftime("%Y-%m-%d")) >= 7:
            item_to_del = db.get_or_404(Cart, item.id)
            db.session.delete(item_to_del)
            db.session.commit()
    return render_template("index.html", products=product, item_num=item_num, fav_items=fav_items)


@app.route('/view_pdt<int:pdt_id>', methods=["GET", "POST"])
def view_pdt(pdt_id):
    global item_num
    result = db.session.execute(db.Select(Cart))
    cart_items = result.scalars().all()
    product = db.get_or_404(Product, pdt_id)

    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash("You need to be Logged in.")
            return redirect(url_for('login'))

        elif product.id == pdt_id:
            if int(request.form['quantity']) <= int(product.stock):
                product.stock -= int(request.form['quantity'])
            else:
                if product.stock != 0:
                    flash(f'Sorry!!!, there is just {product.stock} of this product currently.')
                else:
                    flash(f"Sorry!!!, we don't have this product currently.")
                return redirect(url_for('view_pdt', pdt_id=pdt_id))

        for item in cart_items:
            if item.product_id == pdt_id and current_user.id == item.customer_id:
                item.quantity += int(request.form['quantity'])

                item.product_total = round(product.price * item.quantity, 2)
                db.session.commit()
                return redirect(url_for('cart'))
        new_purchase = Cart(
            product_name=product.name,
            product_id=product.id,
            product_img=product.img_url,
            product_price=product.price,
            product_info=product.about,
            customer_id=current_user.id,
            quantity=request.form['quantity'],
            product_total=product.price * float(request.form['quantity']),
            created=dt.datetime.now().strftime("%Y-%m-%d"),
            modified=dt.datetime.now().strftime("%H:%M:%S")
        )
        db.session.add(new_purchase)
        db.session.commit()
        return redirect(url_for('cart'))

    return render_template("view.html", product=product, item_num=item_num)


@app.route("/cart", methods=["GET", "POST"])
def cart():
    if not current_user.is_authenticated:
        flash("To access your cart, Login please!!!")
        return redirect(url_for('login'))
    total_price = 0
    pt = []
    coupon = 'welcome2024'
    result = db.session.execute(db.Select(Cart))
    cart_items = result.scalars().all()

    for item in cart_items:
        if item.customer_id == current_user.id:
            pdt = db.get_or_404(Product, item.product_id)
            total_price += item.product_total
            pt.append(item.product_total * (pdt.discount / 100))
    discount = sum(pt)
    if request.args.get('coupon') == coupon:
        cpn = total_price - discount
        discount += (5 / 100) * cpn
    elif not request.args.get('coupon') is None:
        flash('This coupon is invalid')
    return render_template('cart.html', item_num=item_num, cart_items=cart_items, total_price=total_price,
                           discount=discount, is_cart=True)


@app.route("/add", methods=["GET", "POST"])
@admin_only
def add_pdt():
    form = ProductPost()
    post_date = dt.datetime.now().strftime("%Y-%m-%d")
    if form.validate_on_submit():
        new_product = Product(
            name=form.name.data,
            in_sale=form.in_sale.data,
            about=form.comment.data,
            discount=form.discount.data,
            price=form.price.data,
            total=form.price.data - (form.discount.data / 100) * form.price.data,
            stock=form.stock.data,
            date=post_date,
            img_url=form.img_url.data
        )
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('make_product.html', form=form, item_num=item_num)


@app.route("/add_favorite<int:id>", methods=["GET", "POST"])
def add_fav(id):
    post_date = dt.datetime.now().strftime("%Y-%m-%d")
    result = db.session.execute(db.Select(Product))
    cart_items = result.scalars().all()
    for _ in range(len(cart_items)):
        pdt = db.get_or_404(Product, id)
        new_fav = Favorite(
            product_id=pdt.id,
            product_price=pdt.price,
            customer_id=current_user.id,
            created=post_date
        )
        db.session.add(new_fav)
        db.session.commit()
        return redirect(url_for('home'))
    return redirect(url_for('home'))


@app.route("/favorite", methods=["GET", "POST"])
def favorite():
    if not current_user.is_authenticated:
        flash("To access your favorites, Login please!!!")
        return redirect(url_for('login'))
    result = db.session.execute(db.Select(Favorite))
    fav_items = result.scalars().all()
    result = db.session.execute(db.Select(Product))
    products = result.scalars().all()

    return render_template('favorite.html', item_num=item_num, fav_items=fav_items, products=products)


@app.route('/edit<int:pdt_id>', methods=['GET', "POST"])
@admin_only
def edit_pdt(pdt_id):
    post_date = dt.datetime.now().strftime("%Y-%m-%d")
    pdt = db.get_or_404(Product, pdt_id)
    edit_form = ProductPost(
        name=pdt.name,
        in_sale=pdt.in_sale,
        comment=pdt.about,
        discount=pdt.discount,
        price=pdt.price,
        total=pdt.price - (pdt.discount / 100) * pdt.price,
        stock=pdt.stock,
        date=post_date,
        img_url=pdt.img_url,
    )
    if edit_form.validate_on_submit():
        pdt.name = edit_form.name.data
        pdt.in_sale = edit_form.in_sale.data
        pdt.about = edit_form.comment.data
        pdt.discount = edit_form.discount.data
        pdt.price = edit_form.price.data
        pdt.total = edit_form.price.data - (edit_form.discount.data / 100) * edit_form.price.data
        pdt.stock = edit_form.stock.data
        pdt.date = post_date
        pdt.img_url = edit_form.img_url.data
        pdt.about = edit_form.comment.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('make_product.html', form=edit_form, is_edit=True, logged_in=current_user, item_num=item_num)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    logged_in = current_user.is_authenticated
    if not logged_in:
        flash("To contact us please log in.")
        return redirect(url_for("home"))
    else:
        if request.method == "POST":
            print(request.form["name"])
            send_email(request.form["name"], request.form["email"], request.form["phone"], request.form["message"])
            return render_template("contact.html", logged_in=current_user.is_authenticated, msg_sent=True,
                                   item_num=item_num)

    return render_template("contact.html", logged_in=current_user.is_authenticated, item_num=item_num)


@app.route('/delete<int:pdt_id>')
@admin_only
def delete(pdt_id):
    result = db.session.execute(db.Select(Favorite))
    favorites = result.scalars().all()

    result = db.session.execute(db.Select(Cart))
    cart_items = result.scalars().all()

    pdt_to_del = db.get_or_404(Product, pdt_id)
    for item in cart_items:
        if item.product_id == pdt_id:
            db.session.delete(item)
            db.session.commit()

    db.session.delete(pdt_to_del)
    db.session.commit()

    for item in favorites:
        if item.product_id == pdt_id:
            del_fav(item.id)

    # fav_to_del = db.session.execute(db.Select(Favorite).where(Favorite.product_id == pdt_id)).scalar()
    # del_fav(fav_to_del.id)
    return redirect(url_for('home'))


@app.route('/delete_item<int:pdt_id>')
def delete_item(pdt_id):
    pdt_to_del = db.get_or_404(Cart, pdt_id)
    pdt = db.get_or_404(Product, pdt_to_del.product_id)
    pdt.stock += pdt_to_del.quantity
    db.session.delete(pdt_to_del)
    db.session.commit()
    return redirect(url_for('cart'))


@app.route('/delete_fav<int:pdt_id>')
def del_fav(pdt_id):
    fav_to_del = db.get_or_404(Favorite, pdt_id)
    db.session.delete(fav_to_del)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/about")
def about():
    return render_template("about.html", logged_in=current_user.is_authenticated, item_num=item_num)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True, port=5004)
