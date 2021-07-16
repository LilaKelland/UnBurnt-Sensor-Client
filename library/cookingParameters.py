from db import db
from cooking_parameters_model import CookingParametersModel

        
 class CookingParameters():

    def __init__(self, user_id):
        self.low_temp_limit = 70
        self.high_temp_limit = 100
        self.check_food_time_interval = 300000
        self.user_id = user_id

    def get_temp_limits_and_check_intervals(self):

        cooking_parameters = CookingParametersModel.find_by_user_id(self.user_id)
        if cooking_parameters:
            self.low_temp_limit = cooking_parameters.low_temp
            self.high_temp_limit = cooking_parameters.high_temp
            self.check_food_time_interval = cooking_parameters.check_time
        return(self.low_temp_limit, self.high_temp_limit, self.check_food_time_interval)