import time

class Timer():

    TOO_HOT_ALERT_INTERVAL = 30
    TOO_COLD_ALERT_INTERVAL = 30
    TOO_COLD_SHUT_DOWN_TIME = 120

    def __init__(self, check_time_interval):
        self.check_food_time_interval = check_time_interval
        self.check_food_timer_starting_timestamp = 0
        self.total_cook_time_starting_timestamp = 0
        self.too_cold_shutdown_timer = 0
        self.too_cold_alert_timer = 0
        self.too_hot_alert_timer = 0
        
    def initialize_timers(self):
        self.total_cook_time_starting_timestamp = time.time()
        self.check_food_timer_starting_timestamp = time.time()

    def reset_timer(self):
        self.check_food_time_interval = 50000
        self.check_food_timer_starting_timestamp = 0
        self.total_cook_time_starting_timestamp = 0
        self.too_cold_shutdown_timer = 0
        self.too_cold_alert_timer = 0
        self.too_hot_alert_timer = 0

    def get_total_cook_time(self):
        return (time.time() - self.total_cook_time_starting_timestamp)

    def get_check_food_timer(self):
        return (time.time()- self.check_food_timer_starting_timestamp)

    def is_check_food_time(self):
        if (time.time() - self.check_food_timer_starting_timestamp) >= self.check_food_time_interval:
            self.check_food_timer_starting_timestamp = time.time()
            return True
        return False

    # def reset_check_food_timer(self):
    #     self.check_food_timer_starting_timestamp = time.time()

    def is_too_cold_alert_time(self):
        if (time.time() - temp_state.too_cold_alert_timer) >= TOO_COLD_ALERT_INTERVAL:
            self.reset_too_cold_alert_timer()
            return True
        return False

    def is_shut_down_time(self):
        return (
            time.time() - self.too_cold_shutdown_timer
        ) >= TOO_COLD_SHUT_DOWN_TIME

    def is_too_hot_alert_time(self):
        if (time.time() - self.too_hot_alert_timer) >= TOO_HOT_ALERT_INTERVAL: 
            self.reset_too_hot_alert_timer()
            return True
        return False

    def reset_too_hot_alert_timer(self):
        self.too_hot_alert_timer = time.time()

    def reset_too_cold_alert_timer(self):
        self.too_cold_alert_timer = time.time()

    def reset_too_cold_shutdown_timer(self):
        self.too_cold_shutdown_timer = time.time()
    
