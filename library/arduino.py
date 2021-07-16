from requests.exceptions import RequestException, Timeout
import requests
import logging
import time
import json
from requests.models import Response

class Arduino:
  """ Gets sensor data from ardunio and caches it if "check_it_now == True". This 
  reduces checking frequency and time to get values for each individual sensor by 2 sec each"""

  def __init__(self):
        self.last_checked = 0
        self.response = ""

  def requests_temp(self, check_it_now = False):
      time_since_checked = time.time() - self.last_checked

      if (time_since_checked < 3) and (check_it_now == False):
        logging.debug("Not calling arduino yet since time_since is {0}".format(time_since_checked))
        return(self.response)

      self.last_checked = time.time()
      try:
        the_response = Response()
        # the_response.code = "expired"
        # the_response.error_type = "expired"
        the_response.status_code = 200
        the_response._content = b'{"left_temp":"69.25","right_temp":"70.0","flame_value":"1023"}'

        self.response = the_response

      
          # self.response = requests.get('http://192.168.4.29:8080/fakeArduino') #("http://192.168.4.28", timeout = 6)#("http://192.168.0.37", timeout = 6)
          # logging.debug(f"Trying to get from arduino and got {self.json.json()}") 
      
      except KeyboardInterrupt as err: # If CTRL+C is pressed, exit cleanly:
        print("Keyboard interrupt")
        print(err)

      except Exception as e:
          logging.warning(f'Getting from Arduino failed with {e}')
          self.response = ''
          
      finally:
          return(self.response)