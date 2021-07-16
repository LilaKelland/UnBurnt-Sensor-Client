""" sensors.py"""

import numpy
from scipy import stats
import math
import logging
from models.sensor_reading_model import SensorReadingModel


class BBQSensor:  

    """grabs individual sensor values and evaluates if NaN"""
#TODO - raise exceptions rather than using dummy (1 and 3 values)

    def __init__(self, value_name, arduino):
        # note: value_name must be string (ie "tempf1")
        self.value_name = value_name
        self.arduino = arduino

    def get_value(self):
        try:
            temp = self.arduino.requests_temp()
            self.value = float(temp.json()[self.value_name])
            count = 0
            while (math.isnan(self.value) == True) and (count < 5):
                temp = self.arduino.requests_temp(True)
                self.value = float(temp.json()[self.value_name])
                count += 1
                logging.info(f'Arduino returned value {self.value} which is nan on count {count}')
            if math.isnan(self.value) == True:
                self.value = 1 #TODO --decide what to do here with this - use raised exceptions instead 

        except Exception as e:  #(RequestException, Timeout):
                logging.warning(f"Got exception {e}")
                self.value = 1 #TODO --decide what to do here with this
    
        return(self.value)

    def is_burning(self):
        pass


class Thermocouple(BBQSensor):
    

    def __init__(self, value_name, arduino, user_id):
    # note: value_name must be string (ie "tempf1")
        self.value_name = value_name
        self.arduino = arduino
        self.slope = 1
        self.BURNING_SLOPE = 4
        self.user_id = user_id


    def _get_time_x(self):
        # get last 3 entries from db
        try:
            result = SensorReadingModel.find_by_user_id(user_id).limit(3).all()
            times = [result.timestamp for _ in result]
            x1 = times[0]
            x2 = times[1]
            x3 = times[2]

        except(IndexError):
            #TODO raise exception
            x1 = 1
            x2 = 1
            x3 = 1
        return(x1, x2, x3)

    def _get_temp_y(self):
        try:
            result = SensorReadingModel.find_by_user_id(user_id).limit(3).all()
            temps = [result.timestamp for _ in result]
            y1 = temps[0]
            y2 = temps[1]
            y3 = temps[2]
     
        except(IndexError):
            #TODO raise exception
            y1 = 1
            y2 = 1
            y3 = 1
        return(y1, y2, y3)

    def temp_slope(self):
        try:
            (x1, x2, x3) = self._get_time_x() 
            (y1, y2, y3) = self._get_temp_y() 
            if (x1, x2, x3 == 1): #TODO if exception raised:
                self.slope = 1
                return(self.slope)
            else:
                self.slope = stats.theilslopes([y1,y2,y3],[x1,x2,x3],0.9) # (ydata,xdata,confidence)  
            
            if self.slope > 1 :
                logging.debug(f'x1: {x1}, x2: {x2}')
                logging.debug(f'y1: {y1}, y2: {y2}')
                logging.debug(f'slope: {self.slope}')

        except: 
            self.slope = 1

        return(self.slope)

    def is_burning(self):
        if self.temp_slope() <= self.BURNING_SLOPE:
            return(False)

        logging.info(f'burning slope: {self.slope}')
        return(True)


class FlameSensor(BBQSensor):
    def __init__(self, value_name, arduino):
    # note: value_name must be string (ie "tempf1")
        self.value_name = value_name
        self.arduino = arduino

    def is_burning(self, flame_value):
        return flame_value < 1023
 

class BBQSensorSet():

    def __init__(self, left, right, flame):
        self.left_thermocouple = left
        self.right_thermocouple = right
        self.flame_sensor = flame
        self.left_temp = 3
        self.is_left_temp_valid = True 
        self.right_temp = 0
        self.is_right_temp_valid = False 
        self.flame_value = 1023
        self.is_flame_valid = True
        self.working_temp = self.left_temp

    def get_left_temp(self): 
        self.left_temp = self.left_thermocouple.get_value()
        self.is_left_temp_valid = self.left_temp not in [1, 32]

    def get_right_temp(self):
        self.right_temp = self.right_thermocouple.get_value()
        self.is_right_temp_valid = self.right_temp not in [1, 32]
    
    def compare_temps(self):
        if self.is_left_temp_valid and self.is_right_temp_valid:
            if abs(self.left_temp - self.right_temp) > 200:
                self.is_left_temp_valid = False
                self.is_right_temp_valid = False
            else:
                self.working_temp = (self.left_temp + self.right_temp)/2

    def lost_thermocouple_connection(self):
        return ((self.is_right_temp_valid == False) and (self.is_left_temp_valid == False))

    def get_flame_value(self): 
        self.flame_value = self.flame_sensor.get_value()
        self.is_flame_valid = self.flame_value >= 50

    def is_bbq_burning(self):
        if ((self.flame_sensor.is_burning(self.flame_value) and self.is_flame_valid == True) or self.left_thermocouple.is_burning() or self.right_thermocouple.is_burning()) :               
            logging.info(f'flame value: {self.flame_value}, is_flame_valid: { self.is_flame_valid}, thermocouple_left_is_burning: {self.left_thermocouple.is_burning()}, right_is_burning: {self.right_thermocouple.is_burning()} ')
            return(True)
        return(False)  

    def get_sensor_readings(self):
        self.get_left_temp()
        self.get_right_temp()
        self.compare_temps()
        self.get_flame_value()