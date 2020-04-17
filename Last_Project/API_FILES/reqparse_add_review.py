from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('reviews', required=True)
parser.add_argument('id_of_user', required=True)