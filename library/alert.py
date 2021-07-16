
import apns2
import logging

class Alert:
    """send APNS alert to ios UnBurnt app (called on state change - tempStateMachine.py)"""
    """ test for outcomes of alerts"""

    def __init__(self, device_token):
        self.device_token = device_token
    
    def start_cooking(self):
        self.send_alert(self.device_token, body = "Up to {}°F.".format(int(bbqSensorSet.working_temp)), title = "Now we're cooking - TIMER STARTED!", sound = "chime", category = "WAS_THERE_FIRE")
    
    def too_cold(self):
        self.send_alert(self.device_token, body = "Cooled down to {}°F.".format(int(bbqSensorSet.working_temp)), title = "Turn UP the BBQ!", sound = 'too_cold.aiff', category = "WAS_THERE_FIRE")

    def too_hot(self):
        self.send_alert(self.device_token, body = "It's {}°F.".format(int(bbqSensorSet.working_temp)), title = "Too HOT!", sound = 'too_hot.aiff', category = "WAS_THERE_FIRE")

    def burning(self):
        self.send_alert(self.device_token, body = "It's {}°F.".format(int(bbqSensorSet.working_temp)), title = "On FIRE!", sound = 'fire.aiff', category = "WAS_THERE_FIRE")

    def shutting_down(self):
        self.send_alert(self.device_token, body = "Shutting down.", title = "Enjoy your food!", sound = 'chime', category = "WAS_THERE_FIRE")

    def lost_sensor_connection(self):
        self.send_alert(self.device_token, body = "Shutting down.", title = "Lost connection with sensors.", sound = 'chime', category = "WAS_THERE_FIRE")

    def timed_food_check(self, check_min, check_sec):
        self.send_alert(self.device_token, body = "How's it looking? Timer resetting.", title = f"{int(check_min)}:{int(check_sec)} Checkpoint", sound = 'radar_timer.aiff', category = "WAS_THERE_FIRE")

    def send_alert(self, device_token, body, title, sound, category):
        cli = apns2.APNSClient(mode = "prod",client_cert = "apns-pro.pem")
        alert = apns2.PayloadAlert(body = body, title = title)
        payload = apns2.Payload(alert = alert, sound = sound, category = category, mutable_content = True)
        n = apns2.Notification(payload = payload, priority = apns2.PRIORITY_LOW)
        for i in range (2):
            response = cli.push(n = n, device_token = device_token[i], topic = 'com.lilakelland.UnBurnt')
            logging.info(f'yay  {i}, {device_token[i]}') 
        logging.debug(f'resoponse status code {response.status_code}')
        assert response.status_code == 200, response.reason
        assert response.apns_id