from data import db_session
from flask import Flask, jsonify
from flask_restful import abort, Api, Resource
from data.reviews import Reviews

from .reqparse_add_review import parser


def abort_if_not_found(review):
    session = db_session.create_session()
    product = session.query(Reviews).filter(Reviews.id == review).first()
    if product is None:
        abort(404, message=f"Review {review} not found")


class ReviewsResource(Resource):
    def get(self, value):
        abort_if_not_found(value)
        session = db_session.create_session()
        review = session.query(Reviews).get(value)
        return jsonify({'review': review.to_dict()})

    def post(self, value):
        args = parser.parse_args()
        session = db_session.create_session()
        rewiew = Reviews(
            reviews=args['reviews'],
            id_of_user=args['id_of_user']
        )
        session.add(rewiew)
        session.commit()
        return jsonify({'success': 'OK'})


class ReviewsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        reviews = session.query(Reviews).all()
        return jsonify({'Reviews': [item.to_dict() for item in reviews]})


class ReviewsDeleteResource(Resource):
    def post(self, value):
        abort_if_not_found(value)
        session = db_session.create_session()
        review = session.query(Reviews).filter(Reviews.id == value).first()
        session.delete(review)
        session.commit()
        return jsonify({'success': 'OK'})
