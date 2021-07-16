from sqlalchemy import Column, String, Integer, Boolean
from base import Base, Session, engine

import sqlalchemy as db

engine = db.create_engine('sqlite:///unburnt.db')
connection = engine.connect()
metadata = db.MetaData()


class TokenModel(Base):
    __tablename__ = 'token'

    token_id = Column(Integer, primary_key=True)
    user_id = Column(String(80))
    token = Column(String(80))

    def __init__(self, user_id, token):
        TokenModel.__table__.create(bind=engine, checkfirst=True)
        self.user_id = user_id
        self.token = token

    def __repr__(self):
        return f'APNS token for with user_id <{self.user_id}>, <{self.token}>'

    def json(self):
        return {'user_id': self.user_id, 'token': self.token}

    def save_to_db(self):
        session = Session
        session.add(self)
        session.commit()
        session.close()

    @classmethod  
    def find_by_user_id(cls, user_id):
        # return cls.query.filter(user_id = user_id).all()
        return Session.query(TokenModel).filter_by(user_id = user_id).all()
