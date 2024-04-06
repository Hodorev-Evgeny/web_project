import datetime
import sqlalchemy
from sqlalchemy import orm

from data.db_session import SqlAlchemyBase


class Message(SqlAlchemyBase):
    __tablename__ = 'messages'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    from_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    to_id = sqlalchemy.Column(sqlalchemy.Integer,
                              sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')
