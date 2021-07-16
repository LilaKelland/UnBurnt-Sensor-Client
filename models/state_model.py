from sqlalchemy import Column, String, Integer, Boolean
from base import Base, Session, engine


class StateModel(Base):
    __tablename__ = 'state'

    state_id = Column(Integer, primary_key=True)
    user_id = Column(String(80))
    state = Column(String(80))

    def __init__(self, user_id, state):
        StateModel.__table__.create(bind=engine, checkfirst=True)
        self.user_id = user_id
        self.state = state

    def __repr__(self):
        return f'Cooking state for with  <{self.user_id}>, <{self.state}> '

    def json(self):
        return {'user_id': self.user_id, 'state': self.state }

    def save_to_db(self):
        session = Session
        session.add(self)
        session.commit()
        session.close()

    @classmethod  
    def find_by_user_id(cls, user_id):
        return Session.query(StateModel).filter_by(user_id = user_id).first()
       

state = StateModel('123', 'cooking')
state.save_to_db()

