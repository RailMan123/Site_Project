from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('name')
parser.add_argument('basket')
parser.add_argument('email')
parser.add_argument('hashed_password')