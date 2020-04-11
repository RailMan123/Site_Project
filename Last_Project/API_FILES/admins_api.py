from .reqparse_user import parser
from data import db_session
from flask import Flask, jsonify
from flask_restful import abort, Api, Resource

from data.users import User

from data.admins import Admin

app = Flask(__name__)
api = Api(app)


def abort_if_product_not_found(admin_id):
    session = db_session.create_session()
    product = session.query(Admin).get(admin_id)
    if not product:
        abort(404, message=f"Admin {admin_id} not found")


class AdminsResource(Resource):
    def get(self, admin):
        abort_if_product_not_found(admin)
        session = db_session.create_session()
        admin = session.query(Admin).filter(Admin.id == admin).first()
        return jsonify({'admin': admin.to_dict()})

    def post(self, admin):
        args = parser.parse_args()
        session = db_session.create_session()
        admin = session.query(Admin).filter(Admin.id == admin).first()
        if not args['name'] is None:
            admin.name = args['name']
        if not args['email'] is None:
            admin.email = args['email']
        if not args['basket'] is None:
            admin.basket = args['basket']
        if not args['hashed_password'] is None:
            Admin.set_password(args['hashed_password'])
        session.commit()
        return jsonify({'success': 'OK'})

    def delete(self, admin):
        abort_if_product_not_found(admin)
        session = db_session.create_session()
        admin = session.query(Admin).get(admin)
        session.delete(admin)
        session.commit()
        return jsonify({'success': 'OK'})

class AddUserResource(Resource):
    pass


class AdminsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        admins = session.query(Admin).all()
        return jsonify({'admins': [user.to_dict() for user in admins]})
