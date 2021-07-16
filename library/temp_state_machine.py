from statemachine import StateMachine, State
# from alert import Alert

import logging
from models.state_model import StateModel


class TempStateMachine(StateMachine):
    """Sstatemachine to handle cooking states and transitions"""
    cold_off = State('Cold', initial=True)
    cooking = State('Cooking')
    cooking_too_hot = State("Cooking_too_hot")
    cooking_too_cold = State("Cooking_too_cold")
    burning = State('Burning')

    def __init__(self, timer, user_id):
        self.timer = timer
        self.user_id = user_id
        super().__init__()

    start_cooking = cold_off.to(cooking) #(when first time temp > _limit)
    temp_dropped_too_cold = cooking.to(cooking_too_cold)
    warmed_back_up = cooking_too_cold.to(cooking)
    temp_too_hot = cooking.to(cooking_too_hot)
    too_hot_to_burn = cooking_too_hot.to(burning)
    cooled_back_down_to_cooking = cooking_too_hot.to(cooking) 
    heat_to_burn = cooking.to(burning) #slope > burning_slope and tempf > high temp_limit
    stop_burning = burning.to(cooking) #when temp < high temp add a too cold warning
    cooled_down_to_turn_off = cooking_too_cold.to(cold_off)
    turn_off = cooking.to(cold_off) #when in cooking and temp too low for 200 sec or more or when both temp sensors invalid
    turn_off_from_too_hot = cooking_too_hot.to(cold_off)

#TODO add in state change time to compare if just changed, leave, 

    def write_state_to_db(self, temp_state):
        state_model = StateModel(self.user_id, temp_state)
        state_model.save_to_db()

    def on_start_cooking(self):
        logging.info("warming up from cold to cooking")
        self.write_state_to_db("cooking")
       
    def on_temp_dropped_too_cold(self):
        logging.info("cooking to too cold")
        self.timer.reset_too_cold_alert_timer()
        self.timer.reset_too_cold_shutdown_timer()
        self.write_state_to_db("cooking_too_cold")

    def on_warmed_back_up(self):
        logging.info("cooking_too_cold.to(cooking)")
        self.write_state_to_db("cooking")

    def on_temp_too_hot(self):
        logging.info("cooking.to(cooking_too_hot)")
        self.timer.reset_too_hot_alert_timer()
        self.write_state_to_db("cooking_too_hot")

    def on_too_hot_to_burn(self):
        logging.info("too hot to burning")
        self.write_state_to_db("burning")
        #TODO - record state (- have triggered by response? slope, temp array and grab user response as to is burning - in API

    def on_cooled_back_down_to_cooking(self):
        logging.info("cooking_too_hot.to(cooking)")
        self.write_state_to_db("cooking")

    def on_heat_to_burn(self):
        logging.info("cooking.to(burning)")       
        # Alert.burning(device_token)
        self.write_state_to_db("burning")
        #TODO - record state (slope, temp array and grab user response as to is buring)

    def on_stop_burning(self):
        logging.info("burning.to(cooking)")
        self.write_state_to_db("cooking")
   
    def on_cooled_down_to_turn_off(self):
        logging.info("cooking_too_cold.to(cold_off)")
        # Alert.shutting_down(device_token)
        self.write_state_to_db("cold_off")
        self.timer.reset_timer()

    def on_turn_off_from_too_hot(self): 
        logging.info("cooking.to(cold_off)")
        # Alert.lost_sensor_connection(device_token)
        self.write_state_to_db("cold_off")
        self.timer.reset_timer()

    def on_turn_off(self):
        logging.info("cooking.to(cold_off)")
        # Alert.lost_sensor_connection(device_token)        
        self.write_state_to_db("cold_off")
        self.timer.reset_timer()