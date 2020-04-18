from flask_restful import reqparse

parser_edit = reqparse.RequestParser()
parser_edit.add_argument('name_of_product')
parser_edit.add_argument("count_of_products")
parser_edit.add_argument('about_product')
parser_edit.add_argument('price_product')
parser_edit.add_argument('sex_category')
parser_edit.add_argument('available_sizes')
parser_edit.add_argument('discount')
parser_edit.add_argument('brands')
parser_edit.add_argument('src_of_img')