from sqlalchemy import Column, String, Integer, Boolean
from base import Base, Session, engine
from library.sensors import BBQSensorSet
from library.timer import Timer
# from temp_state?

class SensorReadingModel(Base):
    __tablename__ = 'display_data'

    display_data_id = Column(Integer, primary_key=True)
    user_id = Column(String(80))
    left_temp = Column(Integer)
    right_temp = Column(Integer)
    working_temp = Column(Integer)
    flame_value = Column(Integer)
    is_left_temp_valid = Column(Boolean)
    is_right_temp_valid = Column(Boolean)
    is_flame_valid = Column(Boolean)
    state = Column(String(20))
    timestamp = Column(Integer)
    total_cook_time = Column(Integer)
    check_food_time = Column(Integer)
    is_actually_on_fire = Column(Boolean)
    

    def __init__(self, user_id, left_temp, is_left_temp_valid, right_temp, is_right_temp_valid, working_temp, flame_value, is_flame_valid, state, timestamp, total_cook_time, check_food_time, is_actually_on_fire=None):
        #TODO *********have temps as optional and:if left is None: self.left_temp = "" else: self.left_temp = left_temp
        SensorReadingModel.__table__.create(bind=engine, checkfirst=True)
        self.user_id = user_id
        self.left_temp = left_temp
        self.is_left_temp_valid = is_left_temp_valid
        self.right_temp = right_temp
        self.is_right_temp_valid = is_right_temp_valid
        self.working_temp = working_temp
        self.flame_value = flame_value
        self.is_flame_valid = is_flame_valid
        self.state = state # only for calculating is on fire later..
        self.total_cook_time = total_cook_time
        self.check_food_time = check_food_time
        self.timestamp = timestamp
        self.is_actually_on_fire = None if is_actually_on_fire is None else is_actually_on_fire

    def __repr__(self):
        return f'Sensor reading for with user_id <{self.user_id}>, <{self.left_temp}>, <{self.is_left_temp_valid}>, <{self.right_temp}, <{self.is_right_temp_valid}, <{self.working_temp}>, <{self.flame_value}>, <{self.is_flame_valid}>, <{self.state}>, <{self.is_actually_on_fire}>'

    # def json(self):
    #     return {'user_id': self.user_id, 'low_temp': self.low_temp 'high_temp': self.high_temp, 'check_time': self.check_time}

    def save_to_db(self):
        session = Session
        session.add(self)
        session.commit()
        session.close()
    

    def save_turned_off_to_db(self, state, timestamp):
        self.state = state
        self.timestamp = timestamp
        self.save_to_db()

    @classmethod  
    def find_by_user_id(cls, user_id):
        # return(cls.query.filter(cls.user_id==user_id).all())
        return Session.query(SensorReadingModel).filter_by(user_id = user_id).all()

    # def delete_from_db(self):
    #     db.display_data.delete(self)
    #     db.display_data.commit()




