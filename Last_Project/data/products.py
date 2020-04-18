import datetime
import sqlalchemy
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Products(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'products'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name_of_product = sqlalchemy.Column(sqlalchemy.String)
    src_of_img = sqlalchemy.Column(sqlalchemy.String, index=True)
    about_product = sqlalchemy.Column(sqlalchemy.String, index=True)
    price_product = sqlalchemy.Column(sqlalchemy.String, index=True)
    sex_category = sqlalchemy.Column(sqlalchemy.String, index=True)
    available_sizes = sqlalchemy.Column(sqlalchemy.String, index=True)
    count_of_products = sqlalchemy.Column(sqlalchemy.Integer, index=True)
    discount = sqlalchemy.Column(sqlalchemy.String, index=True)
    brands = sqlalchemy.Column(sqlalchemy.String, index=True)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                      default=datetime.datetime.now)
