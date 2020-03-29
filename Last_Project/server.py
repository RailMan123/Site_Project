import datetime
from flask import Flask, render_template, jsonify
import datetime
from flask import Flask, render_template, request
from flask_login import LoginManager, login_user, current_user, logout_user, \
    login_required
from flask_wtf import FlaskForm
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from wtforms import PasswordField, BooleanField, SubmitField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from flask import make_response
from data import db_session

from data.products import Products

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
app.config['SECRET_KEY'] = 'my_secret'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route("/")
def main_page():
    connect = db_session.create_session()
    count = 6
    list_of_products = []
    for items in connect.query(Products):
        if count == 0:
            break
        list_of_products.append(items)
        count -= 1
    print(list_of_products[0])
    return render_template('base.html', list_of_products=list_of_products)


@app.route('/product/<int:value>', methods=["GET", "POST"])
def show_product(value):
    pass


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found - 404'}), 404)


if __name__ == "__main__":
    db_session.global_init('db/main_data_base.db')
    app.run()
