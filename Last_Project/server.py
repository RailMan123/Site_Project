import os
import random

from flask import Flask, render_template, jsonify
import datetime
from flask import Flask, render_template, request
from flask_login import LoginManager, login_user, current_user, logout_user, \
    login_required
from flask_ngrok import run_with_ngrok
from flask_restful import Api
from flask_wtf import FlaskForm
from requests import post, get
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from wtforms import PasswordField, BooleanField, SubmitField, StringField, RadioField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from flask import make_response
import logging
from data import db_session
from data.products import Products
from data.users import User
from API_FILES.products_api import ProductsListResource, ProductsResource, ProductsAddResource, ProductDeleteResource
from API_FILES.user_api import UserResource, UserDeleteResource, UsersListResource
from API_FILES.reviews_api import ReviewsResource, ReviewsListResource, ReviewsDeleteResource

# Начало работы
app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
app.config['SECRET_KEY'] = 'very_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
logging.basicConfig(level=logging.INFO)
api = Api(app)
SERVER = 'http://localhost:5000'
DISCOUNT_WORDS = ['sale', 'discount', 'распродажа', 'скид', 'акция', 'дисконт']
MALE_WORDS = ['male', 'муж']
FEMALE_WORDS = ['female', 'жен']


# Функция поиска предметов в форме form_of_search
def search_product(text):
    try:
        if text.isdigit():
            product = get(f'{SERVER}/get_one_product/{text}')
            if product:
                return redirect(f'/product/{text}')
        text = text.lower()
        for i in range(len(DISCOUNT_WORDS)):
            if DISCOUNT_WORDS[i] in text:
                return redirect('/discounts')
        for i in range(len(FEMALE_WORDS)):
            if FEMALE_WORDS[i] in text:
                return redirect('/forfemales')
        for i in range(len(MALE_WORDS)):
            if MALE_WORDS[i] in text:
                return redirect('/formales')
        if 'adidas' in text or 'nike' in text or 'djordan' in text:
            form_of_search = SearchItemForm()
            count = 8
            listt = get(f'{SERVER}/main').json()
            list_of_products = []
            for items in listt['products'][::-1]:
                if count == 0:
                    break
                if text in items['brands']:
                    list_of_products.append(items)
                    count -= 1

            return render_template('index_sorted.html', list_of_products=list_of_products,
                                   form_of_search=form_of_search, how_much_items_in_basket=how_much_items_in_basket())
        listt = get(f'{SERVER}/main').json()
        for i in listt['products'][::-1]:
            if i['name_of_product'].lower() in text or text in i['name_of_product'].lower():
                form_of_search = SearchItemForm()
                count = 8
                list_of_products = []
                for items in listt['products'][::-1]:
                    if count == 0:
                        break
                    try:
                        if items['name_of_product'].lower() in text or text in items['name_of_product'].lower():
                            list_of_products.append(items)
                            count -= 1
                    except:
                        pass
                    random.shuffle(list_of_products)
                return render_template('index_sorted.html', list_of_products=list_of_products,
                                       form_of_search=form_of_search,
                                       how_much_items_in_basket=how_much_items_in_basket())

        return redirect('/')
    except Exception:
        return redirect('/')


# Функция подсчитывающая количество товаров в корзине
def how_much_items_in_basket():
    try:
        if current_user:
            user = get(f'{SERVER}/get_one_user/{current_user.id}').json()['user']
            basket = user['basket']
            if not basket is None and basket != '':
                lenght = basket.split('#')
                count_of_items = 0
                for i in range(len(lenght)):
                    if lenght[i] == '':
                        continue
                    count_of_items += 1
                if count_of_items > 99:
                    return '+'
                return count_of_items
            return 0
        else:
            return 0
    except:
        return 0


# запомнили пользователя
@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


# Выход пользователя
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# Форма поиска предмета
class SearchItemForm(FlaskForm):
    search_item = StringField(validators=[DataRequired()])
    submit_of_search = SubmitField('')


# Главная страница
@app.route("/", methods=["GET", "POST"])
def main_page():
    form_of_search = SearchItemForm()
    if form_of_search.validate_on_submit():
        return search_product(form_of_search.search_item.data)
    count = 8
    listt = get(f'{SERVER}/main').json()
    list_of_products = []
    for items in listt['products'][::-1]:
        if count == 0:
            break
        list_of_products.append(items)
        count -= 1
    return render_template('index.html', list_of_products=list_of_products, form_of_search=form_of_search,
                           how_much_items_in_basket=how_much_items_in_basket())


# Скидки, сортировка
@app.route("/discounts", methods=["GET", "POST"])
def discounts_page():
    form_of_search = SearchItemForm()
    if form_of_search.validate_on_submit():
        return search_product(form_of_search.search_item.data)
    count = 8
    list_of_products = []
    listt = get(f'{SERVER}/main').json()
    for items in listt['products'][::-1]:
        if count == 0:
            break
        try:
            if items['discount'] != '':
                list_of_products.append(items)
                count -= 1
        except:
            pass
        random.shuffle(list_of_products)
    return render_template('index_sorted.html', list_of_products=list_of_products, form_of_search=form_of_search,
                           how_much_items_in_basket=how_much_items_in_basket())


# Мужское, сортировка
@app.route("/formales", methods=["GET", "POST"])
def male_page():
    form_of_search = SearchItemForm()
    if form_of_search.validate_on_submit():
        return search_product(form_of_search.search_item.data)
    count = 8
    list_of_products = []
    listt = get(f'{SERVER}/main').json()
    for items in listt['products'][::-1]:
        if count == 0:
            break
        try:
            if items['sex_category'] == 'men':
                list_of_products.append(items)
                count -= 1
        except:
            pass
        random.shuffle(list_of_products)
    return render_template('index_sorted.html', list_of_products=list_of_products, form_of_search=form_of_search,
                           how_much_items_in_basket=how_much_items_in_basket())


# Женское, сортировка
@app.route("/forfemales", methods=["GET", "POST"])
def female_page():
    form_of_search = SearchItemForm()
    if form_of_search.validate_on_submit():
        return search_product(form_of_search.search_item.data)
    count = 8
    list_of_products = []
    listt = get(f'{SERVER}/main').json()
    for items in listt['products'][::-1]:
        if count == 0:
            break
        try:
            if items['sex_category'] == 'women':
                list_of_products.append(items)
                count -= 1
        except:
            pass
        random.shuffle(list_of_products)
    return render_template('index_sorted.html', list_of_products=list_of_products, form_of_search=form_of_search,
                           how_much_items_in_basket=how_much_items_in_basket())


# Форма добавления пользователем продукта в свою карзину
class ProductForm(FlaskForm):
    submit = SubmitField('Submit')
    example = RadioField('Label',
                         choices=[('38', '38'), ('39', '39'), ('40', '40'), ('41', '41'), ('42', '42'), ('43', '43'),
                                  ('44', '44')])


# Отдельный продукт
@app.route('/product/<int:value>', methods=["GET", "POST"])
def show_product(value):
    connect = db_session.create_session()
    product = get(f'{SERVER}/get_one_product/{value}')
    error_message = ''
    if not product:
        pass
    product = product.json()['product']
    form = ProductForm()
    choices = []
    if product['count_of_products'] <= 0:
        error_message = 'Товара нет на складе...'
    for i in product['available_sizes'].split():
        choices.append((i, i))
    form.example.choices = choices
    if form.validate_on_submit() and current_user.is_authenticated and form.example.data != None:
        user = get(f'{SERVER}/get_one_user/{current_user.id}').json()['user']
        if user['basket'] == None:
            user['basket'] = f"#{value}, {int(form.example.data)}"
            data = {"count_of_products": True}
            response = post(f'{SERVER}/get_one_product/{value}', json=data)
        elif f"{value}, {int(form.example.data)}" not in user['basket'].split('#'):
            user['basket'] = user['basket'] + f'#{value}, {int(form.example.data)}'
            data = {"count_of_products": 'mn'}
            response = post(f'{SERVER}/get_one_product/{value}', json=data)
        print(post(f'{SERVER}/get_one_user/{current_user.id}', json={'basket': user['basket']}).json())
        connect.commit()

    form_of_search = SearchItemForm()
    if form_of_search.validate_on_submit():
        return search_product(form_of_search.search_item.data)
    elif form.validate_on_submit() and not current_user.is_authenticated:
        return redirect('/login')
    return render_template('product.html', product=product, form=form, form_of_search=form_of_search,
                           how_much_items_in_basket=how_much_items_in_basket(), error_message=error_message)


# Ошибка 404
@app.errorhandler(404)
def not_found(error):
    form_of_search = SearchItemForm()
    img_src = '404.png'
    return render_template('errors_page.html', img_src_of_error=img_src, form_of_search=form_of_search)


# Ошибка 500
@app.errorhandler(500)
def not_found(error):
    form_of_search = SearchItemForm()
    img_src = '500.png'
    return render_template('errors_page.html', img_src_of_error=img_src, form_of_search=form_of_search)


# Форма регистрации пользователя
class RegisterForm(FlaskForm):
    email = EmailField('Login / email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat password', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')


# Переход в корзину пользователя
@app.route('/basket', methods=["GET", "POST"])
def show_basket_of_user():
    if not current_user.is_authenticated:
        return redirect('/login')
    else:
        form_of_search = SearchItemForm()
        if form_of_search.validate_on_submit():
            return search_product(form_of_search.search_item.data)
        user = get(f'{SERVER}/get_one_user/{current_user.id}').json()['user']
        rip = user['basket']
        if user['basket'] == None:
            user['basket'] = f""
        new_list_of_items = []
        list_of_items = user['basket'].split('#')
        for i in range(len(list_of_items)):
            if list_of_items[i] != '':
                listt = list(map(int, list_of_items[i].split(', ')))
                intermid = get(f'{SERVER}/get_one_product/{listt[0]}')
                if not intermid:
                    rip = rip.split("#" + ", ".join(map(str, listt)))
                    rip = "".join(rip)
                    continue
                listt[0] = intermid.json()['product']
                new_list_of_items.append(listt)
        user['basket'] = rip
        print(post(f'{SERVER}/get_one_user/{current_user.id}', json={'basket': user['basket']}).json())
        return render_template('basket_of_auth_user.html', list_of_items=new_list_of_items[::-1],
                               form_of_search=form_of_search,
                               how_much_items_in_basket=how_much_items_in_basket())


# Регестрация пользователя
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
            name=form.name.data,
            admin=0,
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


# Форма фвторизации пользователя
class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


# Авторизация пользователя
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user != None and user.check_password(form.password.data):
            login_user(user, remember=True)
            if user.admin != None and user.admin:
                return redirect('/admin_add_product')
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


# Удаление предмета из карзины
@app.route('/basket_item_delete/<int:value_id>/<int:value_size>', methods=["GET", "POST"])
@login_required
def delete_item_from_basket(value_id, value_size):
    user = get(f'{SERVER}/get_one_user/{current_user.id}').json()['user']
    rip = user['basket']
    intermid = ", ".join([str(value_id), str(value_size)])
    rip = rip.split(f"#{intermid}")
    rip = "".join(rip)
    user['basket'] = rip
    data = {"count_of_products": 'pl'}
    response = post(f'{SERVER}/get_one_product/{value_id}', json=data)
    print(post(f'{SERVER}/get_one_user/{current_user.id}', json={'basket': user['basket']}).json())
    return redirect('/basket')


# Форма добавления продукта админом
class AdminAddProduct(FlaskForm):
    name_of_product = StringField('Введите название продукта', validators=[DataRequired()])
    about_product = StringField('Введите информацию о продукте', validators=[DataRequired()])
    price_product = StringField('Введите цену продукта', validators=[DataRequired()])
    sex_category = StringField('men/women', validators=[DataRequired()])
    available_sizes = StringField('Введите размеры через пробел', validators=[DataRequired()])
    discount = StringField('*Необязательное поле, введите цену со скидкой')
    count_of_products = StringField('Введите количество продуктов')
    brands = StringField('Введите производителя, бренд продукта', validators=[DataRequired()])
    submit = SubmitField('Добавить')


# Добавление продукта админом
@app.route('/admin_add_product', methods=["GET", "POST"])
@login_required
def admin_add_product():
    admin_form = AdminAddProduct()
    admin = get(f'{SERVER}/get_one_user/{current_user.id}')
    if not admin or not admin.json()['user']['admin']:
        return redirect('/login')
    admin = admin.json()['user']
    if admin_form.validate_on_submit():
        connect = db_session.create_session()
        last_product = connect.query(Products).order_by(Products.id.desc()).first()
        f = request.files['file']
        file = f"static/img/products-img/product{last_product.id + 1}_photo.png"
        file_name = f"product{last_product.id + 1}_photo.png"
        with open(file, "wb") as fil:
            fil.write(f.read())
        if not admin_form.count_of_products.data.isdigit():
            return render_template('admin_panel_add_product.html', admin_name=admin['name'], admin_email=admin['email'],
                                   title='AdminPanel', form=admin_form, message="Product counts entered incorrectly")
        if not admin_form.price_product.data.isdigit():
            return render_template('admin_panel_add_product.html', admin_name=admin['name'], admin_email=admin['email'],
                                   title='AdminPanel', form=admin_form, message="Product price entered incorrectly")
        if admin_form.discount.data != '' and not admin_form.discount.data.isdigit():
            return render_template('admin_panel_add_product.html', admin_name=admin['name'], admin_email=admin['email'],
                                   title='AdminPanel', form=admin_form, message="Discount field entered incorrectly")
        available_sizes = admin_form.available_sizes.data.split()
        for i in available_sizes:
            if len(i) > 2 and not i.isdigit():
                return render_template('admin_panel_add_product.html', admin_name=admin['name'],
                                       admin_email=admin['email'],
                                       title='AdminPanel', form=admin_form, message="This size does not exist")
        if admin_form.sex_category.data.lower() != 'men' and admin_form.sex_category.data.lower() != 'women' and admin_form.sex_category.data.lower() != 'men/women' and admin_form.sex_category.data.lower() != 'women/men':
            return render_template('admin_panel_add_product.html', admin_name=admin['name'], admin_email=admin['email'],
                                   title='AdminPanel', form=admin_form, message="Sex category entered incorrectly")
        response = post(f'{SERVER}/add_new_product', json={'name_of_product': admin_form.name_of_product.data,
                                                           'about_product': admin_form.about_product.data,
                                                           'price_product': admin_form.price_product.data,
                                                           'sex_category': admin_form.sex_category.data.lower(),
                                                           'available_sizes': admin_form.available_sizes.data,
                                                           'count_of_products': admin_form.count_of_products.data,
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


# Форма изменения существующего продукта админом
class AdminEditProduct(FlaskForm):
    id = StringField('Введите id продукта', validators=[DataRequired()])
    name_of_product = StringField('Введите название продукта')
    about_product = StringField('Введите информацию о продукте')
    price_product = StringField('Введите цену продукта')
    sex_category = StringField('men/women')
    available_sizes = StringField('Введите размеры через пробел')
    count_of_products = StringField('Введите количество товаров')
    discount = StringField('*Необязательное поле, введите цену со скидкой')
    brands = StringField('Введите производителя, бренд продукта')
    submit = SubmitField('Изменить')


# Изменение продукта админом
@app.route('/admin_edit_product', methods=["GET", "POST"])
@login_required
def admin_edit_product():
    admin_form = AdminEditProduct()
    admin = get(f'{SERVER}/get_one_user/{current_user.id}')
    if not admin or not admin.json()['user']['admin']:
        return redirect('/login')
    admin = admin.json()['user']
    if admin_form.validate_on_submit():
        data = {}
        if admin_form.id.data is None or not admin_form.id.data.isdigit():
            return render_template('admin_edit_product.html', admin_name=admin['name'], admin_email=admin['email'],
                                   title='AdminPanel', form=admin_form, message="Choose correct id")
        id = int(admin_form.id.data)
        name_of_product = admin_form.name_of_product.data
        about_product = admin_form.about_product.data
        price_product = admin_form.price_product.data
        sex_category = admin_form.sex_category.data
        available_sizes = admin_form.available_sizes.data
        discount = admin_form.discount.data
        count_of_products = admin_form.count_of_products.data
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
                                       title='AdminPanel', form=admin_form, message="Sex category entered incorrectly")
            data['sex_category'] = sex_category.lower()
        if price_product != '':
            if not price_product.isdigit():
                return render_template('admin_edit_product.html', admin_name=admin['name'],
                                       admin_email=admin['email'],
                                       title='AdminPanel', form=admin_form, message="Product price entered incorrectly")
            data['price_product'] = price_product
        if discount != '':
            if not discount.isdigit():
                return render_template('admin_edit_product.html', admin_name=admin['name'],
                                       admin_email=admin['email'],
                                       title='AdminPanel', form=admin_form,
                                       message="Discount field entered incorrectly")
            data['discount'] = admin_form.discount.data
        if available_sizes != '':
            for i in available_sizes:
                if len(i) > 2 and not i.isdigit():
                    return render_template('admin_edit_product.html', admin_name=admin['name'],
                                           admin_email=admin['email'],
                                           title='AdminPanel', form=admin_form, message="This size does not exist")
            data['available_sizes'] = available_sizes
        if count_of_products != '':
            if not count_of_products.isdigit():
                return render_template('admin_edit_product.html', admin_name=admin['name'],
                                       admin_email=admin['email'],
                                       title='AdminPanel', form=admin_form, message="Enter the number of products")
            data['count_of_products'] = count_of_products
        if request.files['file']:
            f = request.files['file']
            file = f"static/img/products-img/product{admin_form.id.data}_photo.png"
            os.remove(file)
            file_name = f"product{admin_form.id.data}_photo.png"
            with open(file, "wb") as fil:
                fil.write(f.read())
            data['src_of_img'] = file_name
        response = post(f'{SERVER}/get_one_product/{id}', json=data)
        if response:
            return render_template('admin_edit_product.html', admin_name=admin['name'], admin_email=admin['email'],
                                   title='AdminPanel', form=admin_form, message="Success")
        return render_template('admin_edit_product.html', admin_name=admin['name'], admin_email=admin['email'],
                               title='AdminPanel', form=admin_form, message="Something went wrong")
    return render_template('admin_edit_product.html', admin_name=admin['name'], admin_email=admin['email'],
                           title='AdminPanel', form=admin_form, message="")


# Форма удаления продукта админом
class AdminDeletProduct(FlaskForm):
    id = StringField('Введите id продукта', validators=[DataRequired()])
    submit = SubmitField('Удалить')


# Удаление продукта админом
@app.route('/admin_delete_product', methods=["GET", "POST"])
@login_required
def admin_delete_product():
    admin = get(f'{SERVER}/get_one_user/{current_user.id}')
    if not admin or not admin.json()['user']['admin']:
        return redirect('/login')
    admin = admin.json()['user']
    admin_form = AdminDeletProduct()
    if admin_form.validate_on_submit():
        if admin_form.id.data.isdigit():
            id = int(admin_form.id.data)
            response = post(f'{SERVER}/get_one_product/{id}')
            if response:
                response = post(f'{SERVER}/delete_product/{id}')
                file = f"static/img/products-img/product{id}_photo.png"
                os.remove(file)
                if response:
                    return render_template('admin_delete_product.html', admin_name=admin['name'],
                                           admin_email=admin['email'],
                                           title='AdminPanel', form=admin_form, message="Success")
                return render_template('admin_delete_product.html', admin_name=admin['name'],
                                       admin_email=admin['email'],
                                       title='AdminPanel', form=admin_form, message="Something went wrong")
            return render_template('admin_delete_product.html', admin_name=admin['name'],
                                   admin_email=admin['email'],
                                   title='AdminPanel', form=admin_form, message="Something went wrong")
    return render_template('admin_delete_product.html', admin_name=admin['name'], admin_email=admin['email'],
                           title='AdminPanel', form=admin_form, message="")


# Форма удаления пользователя админом
class AdminDeletUser(FlaskForm):
    id = StringField('Введите id пользователя', validators=[DataRequired()])
    submit = SubmitField('Удалить')


# Удаление пользователя
@app.route('/admin_delete_user', methods=["GET", "POST"])
@login_required
def admin_delete_user():
    admin = get(f'{SERVER}/get_one_user/{current_user.id}')
    if not admin or not admin.json()['user']['admin']:
        return redirect('/login')
    admin = admin.json()['user']
    admin_form = AdminDeletUser()
    if admin_form.validate_on_submit():
        if admin_form.id.data.isdigit():
            id = int(admin_form.id.data)
            if_user_admin = get(f'{SERVER}/get_one_user/{id}')
            print(if_user_admin)
            if if_user_admin and int(if_user_admin.json()['user']['admin']) != 1:
                print(if_user_admin.json()['user']['admin'])
                response = post(f'{SERVER}/delete_user/{id}').json()
                if response:
                    return render_template('admin_delete_user.html', admin_name=admin['name'],
                                           admin_email=admin['email'],
                                           title='AdminPanel', form=admin_form, message="Success")
                return render_template('admin_delete_user.html', admin_name=admin['name'], admin_email=admin['email'],
                                       title='AdminPanel', form=admin_form, message="Failed to delete the user")
            return render_template('admin_delete_user.html', admin_name=admin['name'], admin_email=admin['email'],
                                   title='AdminPanel', form=admin_form,
                                   message="The user doesn't exist or you are trying to delete the admin")
        return render_template('admin_delete_user.html', admin_name=admin['name'], admin_email=admin['email'],
                               title='AdminPanel', form=admin_form, message="Check that the data is correct")
    return render_template('admin_delete_user.html', admin_name=admin['name'], admin_email=admin['email'],
                           title='AdminPanel', form=admin_form, message="")


# Форма добавления отзыва
class MakeReview(FlaskForm):
    review = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Опубликовать')


# Отзывы
@app.route('/reviews', methods=["GET", "POST"])
def reviews():
    form_of_search = SearchItemForm()
    form_of_make_review = MakeReview()
    reviews_response = get(f"{SERVER}/all_review").json()
    reviews_list = []
    is_True_admin = 0
    if current_user.is_authenticated:
        id = current_user.id
        response_of_find_user = get(f"{SERVER}/get_one_user/{id}")
        if response_of_find_user:
            is_True_admin = int(response_of_find_user.json()['user']['admin'])
    for data_about_review in reviews_response['Reviews'][::-1]:
        response_of_find_user = get(f"{SERVER}/get_one_user/{data_about_review['id_of_user']}")
        if not response_of_find_user:
            # delete review
            response_of_find_user = post(f"{SERVER}/delete_one_review/{data_about_review['id']}")
            if not response_of_find_user:
                print(response_of_find_user.json())
            continue
        response_of_find_user = response_of_find_user.json()
        data_about_review['name'] = response_of_find_user['user']['name']
        data_about_review['email'] = response_of_find_user['user']['email']
        reviews_list.append(data_about_review)
    if form_of_search.validate_on_submit():
        return search_product(form_of_search.search_item.data)
    if form_of_make_review.validate_on_submit() and current_user.is_authenticated and request.method == 'POST':
        id = current_user.id
        response_of_find_user = get(f"{SERVER}/get_one_user/{id}")
        if not response_of_find_user:
            return render_template("reviews.html", form_of_search=form_of_search, reviews_list=reviews_list,
                                   how_much_items_in_basket=how_much_items_in_basket(),
                                   form_of_make_review=form_of_make_review, message="Вы не зарегестрированы...",
                                   curent_admin=is_True_admin)
        data = {"id_of_user": id, "reviews": form_of_make_review.review.data}
        response = post(f"{SERVER}/one_review/{id}", json=data)
        if not response:
            return render_template("reviews.html", form_of_search=form_of_search, reviews_list=reviews_list,
                                   how_much_items_in_basket=how_much_items_in_basket(),
                                   form_of_make_review=form_of_make_review, message="Что-то пошло не так...",
                                   curent_admin=is_True_admin)
        form_of_make_review.review.data = ''
        return redirect("/reviews")
    elif form_of_make_review.validate_on_submit() and not current_user.is_authenticated:
        return redirect("/login")

    return render_template("reviews.html", form_of_search=form_of_search, reviews_list=reviews_list,
                           how_much_items_in_basket=how_much_items_in_basket(), form_of_make_review=form_of_make_review,
                           message="", curent_admin=is_True_admin)


# Удаление отзыва
@app.route('/delete_one_review/<int:value>')
def delete_reviews(value):
    r = post(f"{SERVER}/delete_one_review/{value}")
    return redirect('/reviews')


if __name__ == "__main__":
    # Подключение базы данных, api и запуск приложения
    db_session.global_init('db/main_data_base.db')
    api.add_resource(ProductsListResource, '/main')
    api.add_resource(ProductsResource, f'/get_one_product/<int:value>')
    api.add_resource(UserResource, f'/get_one_user/<int:user>')
    api.add_resource(ReviewsResource, f'/one_review/<int:value>')
    api.add_resource(ReviewsListResource, f'/all_review')
    api.add_resource(ProductsAddResource, f'/add_new_product')
    api.add_resource(ReviewsDeleteResource, f'/delete_one_review/<int:value>')
    api.add_resource(ProductDeleteResource, f'/delete_product/<int:value>')
    api.add_resource(UserDeleteResource, f'/delete_user/<int:user>')
    app.run()
