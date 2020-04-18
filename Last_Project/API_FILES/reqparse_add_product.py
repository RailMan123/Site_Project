from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('name_of_product', required=True)
parser.add_argument('about_product', required=True)
parser.add_argument('price_product', required=True)
parser.add_argument('sex_category', required=True)
parser.add_argument('available_sizes', required=True)
parser.add_argument('discount')
parser.add_argument("count_of_products", required=True)
parser.add_argument('brands', required=True)
parser.add_argument('src_of_img', required=True)
