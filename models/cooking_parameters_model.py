from sqlalchemy import Column, String, Integer, Boolean
from base import Base, Session, engine

class CookingParametersModel(Base):
    __tablename__ = 'cooking_parameters'

    cooking_parameters_id = Column(Integer, primary_key=True)
    user_id = Column(String(80))
    low_temp = Column(Integer)
    high_temp = Column(Integer)
    check_time = Column(Integer)

    def __init__(self, user_id, low_temp, high_temp, check_time):
        CookingParametersModel.__table__.create(bind=engine, checkfirst=True)
        self.user_id = user_id
        self.low_temp = low_temp
        self.high_temp = high_temp
        self.check_time = check_time

    def __repr__(self):
        return f'Cooking Parameters for with user_id <{self.user_id}>, <{self.low_temp}>, <{self.high_temp}>, <{check_time}>'

    def json(self):
        return {'user_id': self.user_id, 'low_temp': self.low_temp, 'high_temp': self.high_temp, 'check_time': self.check_time}

    def save_to_db(self):
        session = Session
        session.add(self)
        session.commit()
        session.close()

    @classmethod  
    def find_by_user_id(cls, user_id):
        # return(cls.query.filter(cls.user_id==user_id).all())
        return Session.query(CookingParametersModel).filter_by(user_id = user_id).first()



class CookingParameters:

    def __init__(self, user_id):
        self.low_temp_limit = 70
        self.high_temp_limit = 100
        self.check_food_time_interval = 300000
        self.user_id = user_id

    def get_temp_limits_and_check_intervals(self):

        if CookingParametersModel.find_by_user_id(self.user_id) is None:
            return(self.low_temp_limit, self.high_temp_limit, self.check_food_time_interval)
        user_id, low_temp_limit, high_temp_limit, check_food_time_interval = CookingParametersModel.find_by_user_id(self.user_id)
        if low_temp_limit != None:
            self.low_temp_limit = low_temp_limit
        if high_temp_limit != None:
            self.high_temp_limit = high_temp_limit
        if check_food_time_interval != None:
            self.check_food_time_interval = check_food_time_interval

        return(self.low_temp_limit, self.high_temp_limit, self.check_food_time_interval)