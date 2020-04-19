from data import db_session
from flask import Flask, jsonify
from flask_restful import abort, Api, Resource
from data.products import Products

from .reqparse_add_product import parser
from .reqparse_edit_product import parser_edit

app = Flask(__name__)
api = Api(app)


def abort_if_not_found(product_id):
    session = db_session.create_session()
    product = session.query(Products).filter(Products.id == product_id).first()
    if product is None:
        abort(404, message=f"Users {product_id} not found")


class ProductsResource(Resource):
    def get(self, value):
        abort_if_not_found(value)
        session = db_session.create_session()
        product = session.query(Products).get(value)
        return jsonify({'product': product.to_dict()})

    def post(self, value):
        abort_if_not_found(value)
        session = db_session.create_session()
        args = parser_edit.parse_args()
        product = session.query(Products).filter(Products.id == value).first()
        if not args['name_of_product'] is None:
            product.name_of_product = args['name_of_product']
        if not args['about_product'] is None:
            product.about_product = args['about_product']
        if not args['price_product'] is None:
            product.price_product = args['price_product']
        if not args['sex_category'] is None:
            product.sex_category = args['sex_category']
        if not args['available_sizes'] is None:
            product.available_sizes = args['available_sizes']
        if not args['discount'] is None:
            product.discount = args['discount']
        if not args['count_of_products'] is None:
            if args['count_of_products'].isdigit():
                product.count_of_products = int(args['count_of_products'])
            elif args['count_of_products'] == 'pl':
                product.count_of_products += 1
            elif args['count_of_products'] == 'mn':
                product.count_of_products -= 1
        if not args['brands'] is None:
            product.brands = args['brands']
        if not args['src_of_img'] is None:
            product.src_of_img = args['src_of_img']
        session.commit()
        return jsonify({'success': 'OK'})


class ProductsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        products = session.query(Products).all()
        return jsonify({'products': [item.to_dict() for item in products]})


class ProductDeleteResource(Resource):
    def post(self, value):
        abort_if_not_found(value)
        session = db_session.create_session()
        product = session.query(Products).get(value)
        session.delete(product)
        session.commit()
        return jsonify({'success': 'OK'})


class ProductsAddResource(Resource):
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        product = Products(
            name_of_product=args['name_of_product'],
            about_product=args['about_product'],
            src_of_img=args['src_of_img'],
            price_product=args['price_product'],
            sex_category=args['sex_category'],
            count_of_products=args['count_of_products'],
            available_sizes=args['available_sizes'],
            brands=args['brands'],
        )
        if not args['discount'] is None:
            product.discount = args['discount']
        session.add(product)
        session.commit()
        return jsonify({'success': 'OK'})
