from data import db_session
from flask import Flask, jsonify
from flask_restful import abort, Api, Resource

from data.products import Products

app = Flask(__name__)
api = Api(app)


def abort_if_product_not_found(product_id):
    session = db_session.create_session()
    product = session.query(Products).get(product_id)
    if not product:
        abort(404, message=f"Product {product_id} not found")


class ProductsResource(Resource):
    def get(self, product):
        abort_if_product_not_found(product)
        session = db_session.create_session()
        user = session.query(Products).get(product)
        return jsonify({'product': user.to_dict()})

    def delete(self, product):
        abort_if_product_not_found(product)
        session = db_session.create_session()
        user = session.query(Products).get(product)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class ProductsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        products = session.query(Products).all()
        return jsonify({'products': [item.to_dict() for item in products]})