"""UnBurnt.py

Always running on server - will start alerting phone once in cooking state, 
and will automaticaly go back to cold (sleep) state once BBQ has cooled down.

Run with app.py """

import logging
import time
from library.alert import Alert
from library.temp_state_machine import TempStateMachine

# from cookingParameters import CookingParameters - use model and CookingParameters.find_by_user_id??
from library.sensors import BBQSensorSet, Thermocouple, FlameSensor
from library.timer import Timer
from library.arduino import Arduino
from models.cooking_parameters_model import CookingParameters
from models.sensor_reading_model import SensorReadingModel
# from models.state_model import StateModel
from models.token_model import TokenModel

import requests

# import psycopg2
# from unburnt_db import db

from base import engine, Base

# import db as db
import sqlalchemy as db

engine = db.create_engine("sqlite:///unburnt.db")
connection = engine.connect()

Base.metadata.create_all(engine)
# session = Session()

logging.basicConfig(level=logging.WARNING)

# TODO --store this in a DB and associate with user id allow for varying number of device token

user_id = 123
device_token = []
for i in TokenModel.find_by_user_id(user_id):
    logging.info(i)
    device_token.append(i["token"])

device_token = [1234, 5678]

logging.info(device_token)

user_id = 123

alert = Alert(device_token)
timer = Timer(50000)

temp_state = TempStateMachine(timer, user_id)
arduino = Arduino()

thermocouple_left = Thermocouple("left_temp", arduino)
thermocouple_right = Thermocouple("right_temp", arduino)
flame_sensor = FlameSensor("flame_value", arduino)

bbqSensorSet = BBQSensorSet(thermocouple_left, thermocouple_right, flame_sensor)

cooking_parameters = CookingParameters(123)

# TODO need to feed user_id in cooking parameters - do we need to retreive from token first?


while True:
    (
        low_temp_limit,
        high_temp_limit,
        timer.check_food_time_interval,
    ) = cooking_parameters.get_temp_limits_and_check_intervals()

    # when in cold/ off state
    if temp_state.is_cold_off:
        # TODO changed from temp_state.is_cold_off??

        # logging.debug(f"{temp_state.current_state}")
        # logging.debug(f"working temps  {bbqSensorSet.working_temp}")
        # logging.debug(
        #     f"{bbqSensorSet.left_temp}, {bbqSensorSet.is_left_temp_valid}, {bbqSensorSet.right_temp}, {bbqSensorSet.is_right_temp_valid}, {bbqSensorSet.flame_value}, {bbqSensorSet.is_flame_valid}"
        # )
        logging.debug('%s', temp_state.current_state)
        logging.debug("working temps %s",  bbqSensorSet.working_temp)
        logging.debug('%s', (bbqSensorSet.left_temp, bbqSensorSet.is_left_temp_valid, bbqSensorSet.right_temp, bbqSensorSet.is_right_temp_valid, bbqSensorSet.flame_value, bbqSensorSet.is_flame_valid))

        bbqSensorSet.get_sensor_readings()

        if bbqSensorSet.working_temp > low_temp_limit:
            timer.initialize_timers()
            alert.start_cooking()
            temp_state.start_cooking()
            continue

    # for all states other than cold
    else:
        try:
            # check the check-food timer, and reset if interval reached
            if timer.is_check_food_time():
                check_min, check_sec = divmod(timer.get_check_food_timer(), 60)
                alert.timed_food_check(check_min, check_sec)

            # read sensors & update ios dashboard display data
            bbqSensorSet.get_sensor_readings()
            sensor_reading = SensorReadingModel(
                user_id,
                bbqSensorSet.left_temp,
                bbqSensorSet.is_left_temp_valid,
                bbqSensorSet.right_temp,
                bbqSensorSet.is_right_temp_valid,
                bbqSensorSet.working_temp,
                bbqSensorSet.flame_value,
                bbqSensorSet.is_flame_valid,
                temp_state.current_state,
                time.time(),
                timer.get_total_cook_time(),
                timer.get_check_food_timer(),
            )

            if bbqSensorSet.lost_thermocouple_connection():
                logging.info("temperature sensors offline, shutting down.")
                alert.lost_sensor_connection()
                timer.reset_timer()
                sensor_reading.save_turned_off_to_db(time.time(), "Cold")
                temp_state.turn_off()
                continue

            sensor_reading.save_to_db()
            # TODO - separate out non-"sensor" readings into alternate tables and join when needed later for displays

            # when in "cooking" State:
            if temp_state.is_cooking:
                if bbqSensorSet.working_temp < low_temp_limit:
                    alert.too_cold()
                    timer.reset_too_cold_alert_timer()
                    timer.reset_too_cold_shutdown_timer()
                    temp_state.temp_dropped_too_cold()

                elif bbqSensorSet.working_temp > high_temp_limit:
                    alert.too_hot()
                    timer.reset_too_hot_alert_timer()
                    temp_state.temp_too_hot()

                if bbqSensorSet.is_bbq_burning():
                    alert.burning()
                    temp_state.heat_to_burn()

            # when in "cooking_too_cold" state
            if temp_state.is_cooking_too_cold:

                if timer.is_too_cold_alert_time():
                    alert.too_cold()

                elif timer.is_shut_down_time():
                    alert.shutting_down()
                    sensor_reading.save_turned_off_to_db(time.time(), "Cold")
                    timer.reset_timer()
                    temp_state.cooled_down_to_turn_off()

                if bbqSensorSet.working_temp > low_temp_limit:
                    temp_state.warmed_back_up()

            # when in "cooking_too_hot" state
            if temp_state.is_cooking_too_hot:

                if timer.is_too_hot_alert_time() == True:
                    alert.too_hot()

                if bbqSensorSet.is_bbq_burning() == True:
                    alert.burning()
                    temp_state.heat_to_burn()

                elif bbqSensorSet.working_temp < high_temp_limit:
                    temp_state.cooled_back_down_to_cooking()

            # when in burning state
            if temp_state.is_burning:
                alert.burning()
                if (bbqSensorSet.working_temp < high_temp_limit) and (
                    not flame_sensor.is_burning(bbqSensorSet.flame_value)
                ):
                    # if not bbqSensorSet.is_bbq_burning():
                    temp_state.stop_burning()

        except requests.RequestException as e:
            logging.warning("network error with sensor %s", e)
