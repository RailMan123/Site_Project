import os

from flask import Flask, render_template, jsonify
import datetime
from flask import Flask, render_template, request
from flask_login import LoginManager, login_user, current_user, logout_user, \
    login_required
from flask_restful import Api
from flask_wtf import FlaskForm
from requests import post, get
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from wtforms import PasswordField, BooleanField, SubmitField, StringField, RadioField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from flask import make_response
import logging
from data import db_session
from data.products import Products
from data.users import User
from API_FILES.products_api import ProductsListResource, ProductsResource
from API_FILES.user_api import UserResource
from API_FILES.admins_api import AdminsResource
from data.admins import Admin

from API_FILES.products_api import ProductsAddResource

from API_FILES.products_api import ProductDeleteResource

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
app.config['SECRET_KEY'] = 'my_secret'

login_manager = LoginManager()
login_manager.init_app(app)

# logging.basicConfig(level=logging.INFO)

api = Api(app)
SERVER = 'http://localhost:5000'


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


class SearchItemForm(FlaskForm):
    search_item = StringField(validators=[DataRequired()])
    submit_of_search = SubmitField('')


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.route("/", methods=["GET", "POST"])
def main_page():
    form = SearchItemForm()

    if form.validate_on_submit():
        print(form.search_item.data)
    count = 9
    listt = get(f'{SERVER}/main').json()
    list_of_products = []
    for items in listt['products'][::-1]:
        if count == 0:
            break
        list_of_products.append(items)
        count -= 1
    # form_of_search=form
    return render_template('index.html', list_of_products=list_of_products)


@app.route("/formales")
def male_page():
    connect = db_session.create_session()
    count = 6
    list_of_products = []
    for items in connect.query(Products):
        if count == 0:
            break
        try:
            if items.sax_cat == 'male':
                list_of_products.append(items)
                count -= 1
        except:
            pass
    return render_template('index.html', list_of_products=list_of_products)


@app.route("/forfemales")
def female_page():
    connect = db_session.create_session()
    count = 9
    list_of_products = []
    for items in connect.query(Products):
        if count == 0:
            break
        try:
            if items.sax_cat == 'female':
                list_of_products.append(items)
                count -= 1
        except:
            pass
    return render_template('index.html', list_of_products=list_of_products)


@app.route("/discounts")
def discounts_page():
    connect = db_session.create_session()
    count = 9
    list_of_products = []
    for items in connect.query(Products):
        if count == 0:
            break
        try:
            if items.discount != None:
                print(items.discount)
                list_of_products.append(items)
                count -= 1
        except:
            pass
    return render_template('index.html', list_of_products=list_of_products)


class ProductForm(FlaskForm):
    submit = SubmitField('Submit')
    example = RadioField('Label',
                         choices=[('38', '38'), ('39', '39'), ('40', '40'), ('41', '41'), ('42', '42'), ('43', '43'),
                                  ('44', '44')])


@app.route('/product/<int:value>', methods=["GET", "POST"])
def show_product(value):
    connect = db_session.create_session()
    product = get(f'{SERVER}/get_one_product/{value}').json()['product']
    form = ProductForm()
    if form.validate_on_submit() and current_user.is_authenticated and form.example.data != None:
        user = get(f'{SERVER}/get_one_user/{current_user.id}').json()['user']
        if user['basket'] == None:
            user['basket'] = f"#{value}, {int(form.example.data)}"
        elif f"{value}, {int(form.example.data)}" not in user['basket'].split('#'):
            user['basket'] = user['basket'] + f'#{value}, {int(form.example.data)}'
        print(post(f'{SERVER}/get_one_user/{current_user.id}', json={'basket': user['basket']}).json())
        connect.commit()
    elif form.validate_on_submit() and not current_user.is_authenticated:
        return redirect('/login')
    return render_template('product.html', product=product, form=form)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found - 404'}), 404)


class RegisterForm(FlaskForm):
    email = EmailField('Login / email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat password', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/basket', methods=["GET", "POST"])
def show_basket_of_user():
    if not current_user.is_authenticated:
        return redirect('/login')
    else:
        user = get(f'{SERVER}/get_one_user/{current_user.id}').json()['user']
        print(user)
        rip = user['basket']
        new_list_of_items = []
        list_of_items = user['basket'].split('#')
        for i in range(len(list_of_items)):
            if list_of_items[i] != '':
                listt = list(map(int, list_of_items[i].split(', ')))
                intermid = get(f'{SERVER}/get_one_product/{listt[0]}').json()
                if 'error' in intermid:
                    rip = rip.split("#" + ", ".join(map(str, listt)))
                    rip = "".join(rip)
                    continue
                listt[0] = intermid['product']
                new_list_of_items.append(listt)
        user['basket'] = rip
        print(post(f'{SERVER}/get_one_user/{current_user.id}', json={'basket': user['basket']}).json())
        return render_template('basket_of_auth_user.html', list_of_items=new_list_of_items[::-1])


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            email=form.email.data,
            name=form.name.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        admin = session.query(User).filter(Admin.email == form.email.data).first()
        if admin and admin.check_password(form.password.data):
            login_user(admin, remember=form.remember_me.data)
            return redirect('/admin_add_product')
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/basket_item_delete/<int:value_id>/<int:value_size>', methods=["GET", "POST"])
@login_required
def delete_item_from_basket(value_id, value_size):
    user = get(f'{SERVER}/get_one_user/{current_user.id}').json()['user']
    rip = user['basket']
    intermid = ", ".join([str(value_id), str(value_size)])
    rip = rip.split(f"#{intermid}")
    rip = "".join(rip)
    user['basket'] = rip
    print(post(f'{SERVER}/get_one_user/{current_user.id}', json={'basket': user['basket']}).json())
    return redirect('/basket')


class AdminAddProduct(FlaskForm):
    name_of_product = StringField('Введите название продукта', validators=[DataRequired()])
    about_product = StringField('Введите информацию о продукте', validators=[DataRequired()])
    price_product = StringField('Введите цену продукта', validators=[DataRequired()])
    sex_category = StringField('men/women', validators=[DataRequired()])
    available_sizes = StringField('Введите размеры через пробел', validators=[DataRequired()])
    discount = StringField('*Необязательное поле, введите цену со скидкой')
    brands = StringField('Введите производителя, бренд продукта', validators=[DataRequired()])
    submit = SubmitField('Добавить')


@app.route('/admin_add_product', methods=["GET", "POST"])
@login_required
def admin_add_product():
    admin_form = AdminAddProduct()
    admin = get(f'{SERVER}/get_one_admin/{current_user.id}').json()
    if 'error' in admin:
        return redirect('/login')
    admin = admin['admin']
    if admin_form.validate_on_submit():
        connect = db_session.create_session()
        last_product = connect.query(Products).order_by(Products.id.desc()).first()
        f = request.files['file']
        file = f"static/img/products-img/product{last_product.id + 1}_photo.png"
        file_name = f"product{last_product.id + 1}_photo.png"
        with open(file, "wb") as fil:
            fil.write(f.read())
        if not admin_form.price_product.data.isdigit():
            return render_template('admin_panel_add_product.html', admin_name=admin['name'], admin_email=admin['email'],
                                   title='AdminPanel', form=admin_form, message="Data entered incorrectly")
        if admin_form.discount.data != '' and not admin_form.discount.data.isdigit():
            return render_template('admin_panel_add_product.html', admin_name=admin['name'], admin_email=admin['email'],
                                   title='AdminPanel', form=admin_form, message="Data entered incorrectly")
        available_sizes = admin_form.available_sizes.data.split()
        for i in available_sizes:
            if len(i) > 2 and not i.isdigit():
                return render_template('admin_panel_add_product.html', admin_name=admin['name'],
                                       admin_email=admin['email'],
                                       title='AdminPanel', form=admin_form, message="This size does not exist")
        if admin_form.sex_category.data.lower() != 'men' and admin_form.sex_category.data.lower() != 'women' and admin_form.sex_category.data.lower() != 'men/women' and admin_form.sex_category.data.lower() != 'women/men':
            return render_template('admin_panel_add_product.html', admin_name=admin['name'], admin_email=admin['email'],
                                   title='AdminPanel', form=admin_form, message="Data entered incorrectly")
        response = post(f'{SERVER}/add_new_product', json={'name_of_product': admin_form.name_of_product.data,
                                                           'about_product': admin_form.about_product.data,
                                                           'price_product': admin_form.price_product.data,
                                                           'sex_category': admin_form.sex_category.data.lower(),
                                                           'available_sizes': admin_form.available_sizes.data,
                                                           'discount': admin_form.discount.data,
                                                           'brands': admin_form.brands.data,
                                                           'src_of_img': file_name})
        if response:
            return render_template('admin_panel_add_product.html', admin_name=admin['name'], admin_email=admin['email'],
                                   title='AdminPanel', form=admin_form, message="Success")
        else:
            return render_template('admin_panel_add_product.html', admin_name=admin['name'], admin_email=admin['email'],
                                   title='AdminPanel', form=admin_form, message="Something went wrong")
    return render_template('admin_panel_add_product.html', admin_name=admin['name'], admin_email=admin['email'],
                           title='AdminPanel', form=admin_form, message="")


class AdminEditProduct(FlaskForm):
    id = StringField('Введите id продукта', validators=[DataRequired()])
    name_of_product = StringField('Введите название продукта')
    about_product = StringField('Введите информацию о продукте')
    price_product = StringField('Введите цену продукта')
    sex_category = StringField('men/women')
    available_sizes = StringField('Введите размеры через пробел')
    discount = StringField('*Необязательное поле, введите цену со скидкой')
    brands = StringField('Введите производителя, бренд продукта')
    submit = SubmitField('Изменить')


@app.route('/admin_edit_product', methods=["GET", "POST"])
@login_required
def admin_edit_product():
    admin_form = AdminEditProduct()
    admin = get(f'{SERVER}/get_one_admin/{current_user.id}').json()
    if 'error' in admin:
        return redirect('/login')
    admin = admin['admin']
    if admin_form.validate_on_submit():
        data = {}
        if admin_form.id.data is None or not admin_form.id.data.isdigit():
            return render_template('admin_edit_product.html', admin_name=admin['name'], admin_email=admin['email'],
                                   title='AdminPanel', form=admin_form, message="Data entered incorrectly")
        id = int(admin_form.id.data)
        print(id)
        name_of_product = admin_form.name_of_product.data
        about_product = admin_form.about_product.data
        price_product = admin_form.price_product.data
        sex_category = admin_form.sex_category.data
        available_sizes = admin_form.available_sizes.data
        discount = admin_form.discount.data
        brands = admin_form.brands.data
        if name_of_product != '':
            data['name_of_product'] = name_of_product
        if about_product != '':
            data['about_product'] = about_product
        if brands != '':
            data['brands'] = admin_form.brands.data
        if sex_category != '':
            if sex_category.lower() != 'men' and sex_category.lower() != 'women' and sex_category.lower() != 'men/women' and sex_category.lower() != 'women/men':
                return render_template('admin_edit_product.html', admin_name=admin['name'],
                                       admin_email=admin['email'],
                                       title='AdminPanel', form=admin_form, message="Data entered incorrectly")
            data['sex_category'] = sex_category.lower()
        if price_product != '':
            if not price_product.isdigit():
                return render_template('admin_edit_product.html', admin_name=admin['name'],
                                       admin_email=admin['email'],
                                       title='AdminPanel', form=admin_form, message="Data entered incorrectly")
            data['price_product'] = price_product
        if discount != '':
            if not discount.isdigit():
                return render_template('admin_edit_product.html', admin_name=admin['name'],
                                       admin_email=admin['email'],
                                       title='AdminPanel', form=admin_form, message="Data entered incorrectly")
            data['discount'] = admin_form.discount.data
        if available_sizes != '':
            for i in available_sizes:
                if len(i) > 2 and not i.isdigit():
                    return render_template('admin_edit_product.html', admin_name=admin['name'],
                                           admin_email=admin['email'],
                                           title='AdminPanel', form=admin_form, message="This size does not exist")
            data['available_sizes'] = available_sizes
        if request.files['file']:
            f = request.files['file']
            file = f"static/img/products-img/product{admin_form.id.data}_photo.png"
            os.remove(file)
            file_name = f"product{admin_form.id.data}_photo.png"
            with open(file, "wb") as fil:
                fil.write(f.read())
            data['src_of_img'] = file_name
        response = post(f'{SERVER}/get_one_product/{id}', json=data)
        print(response)
        if response:
            return render_template('admin_edit_product.html', admin_name=admin['name'], admin_email=admin['email'],
                                   title='AdminPanel', form=admin_form, message="Success")
        return render_template('admin_edit_product.html', admin_name=admin['name'], admin_email=admin['email'],
                               title='AdminPanel', form=admin_form, message="Something went wrong")
    return render_template('admin_edit_product.html', admin_name=admin['name'], admin_email=admin['email'],
                           title='AdminPanel', form=admin_form, message="")


class AdminDeletProduct(FlaskForm):
    id = StringField('Введите id продукта', validators=[DataRequired()])
    submit = SubmitField('Удалить')


@app.route('/admin_delete_product', methods=["GET", "POST"])
@login_required
def admin_delete_product():
    admin = get(f'{SERVER}/get_one_admin/{current_user.id}').json()
    if 'error' in admin:
        return redirect('/login')
    admin = admin['admin']
    admin_form = AdminDeletProduct()
    if admin_form.validate_on_submit():
        if admin_form.id.data.isdigit():
            id = int(admin_form.id.data)
            response = post(f'{SERVER}/delete_product/{id}')
            file = f"static/img/products-img/product{id}_photo.png"
            os.remove(file)
            if response:
                return render_template('admin_delete_product.html', admin_name=admin['name'],
                                       admin_email=admin['email'],
                                       title='AdminPanel', form=admin_form, message="Success")
            return render_template('admin_delete_product.html', admin_name=admin['name'], admin_email=admin['email'],
                                   title='AdminPanel', form=admin_form, message="Something went wrong")
    return render_template('admin_delete_product.html', admin_name=admin['name'], admin_email=admin['email'],
                           title='AdminPanel', form=admin_form, message="")


if __name__ == "__main__":
    db_session.global_init('db/main_data_base.db')
    api.add_resource(ProductsListResource, '/main')
    api.add_resource(ProductsResource, f'/get_one_product/<int:value>')
    api.add_resource(UserResource, f'/get_one_user/<int:user>')
    api.add_resource(AdminsResource, f'/get_one_admin/<int:admin>')
    api.add_resource(ProductsAddResource, f'/add_new_product')
    api.add_resource(ProductDeleteResource, f'/delete_product/<int:value>')
    app.run()

# {{ form_of_search.hidden_tag() }}
# {{ form_of_search.csrf_token }}
# {{ form_of_search.search_item }}
# {{ form_of_search.submit_of_search(class="img_of_search")}}
