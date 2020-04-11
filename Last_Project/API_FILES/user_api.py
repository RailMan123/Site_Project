from .reqparse_user import parser
from data import db_session
from flask import Flask, jsonify
from flask_restful import abort, Api, Resource

from data.users import User

app = Flask(__name__)
api = Api(app)


def abort_if_product_not_found(user_id):
    session = db_session.create_session()
    product = session.query(User).get(user_id)
    if not product:
        abort(404, message=f"User {user_id} not found")


class UserResource(Resource):
    def get(self, user):
        abort_if_product_not_found(user)
        session = db_session.create_session()
        user = session.query(User).get(user)
        return jsonify({'user': user.to_dict()})

    def post(self, user):
        args = parser.parse_args()
        session = db_session.create_session()
        user = session.query(User).filter(User.id == user).first()
        if not args['name'] is None:
            user.name = args['name']
        if not args['email'] is None:
            user.email = args['email']
        if not args['basket'] is None:
            user.basket = args['basket']
        if not args['hashed_password'] is None:
            User.set_password(args['hashed_password'])
        session.commit()
        return jsonify({'success': 'OK'})

    def delete(self, user):
        abort_if_product_not_found(user)
        session = db_session.create_session()
        user = session.query(User).get(user)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UserDeleteResource(Resource):
    def post(self, user):
        abort_if_product_not_found(user)
        session = db_session.create_session()
        user = session.query(User).get(user)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [user.to_dict() for user in users]})
