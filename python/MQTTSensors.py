'''
Thin wrapper to create mqtt sensor data message
Author: Howard Webb
Date: 7/10/2021
'''

from Sensor import Sensors
from mqttUtil import pingMQTT
import json

# sub-topic name
name = "sensors_values"

# Get sensor object for data
s = Sensors()
# Get json structure of values
msg = s.get_full()
# Convert json to string
msg2 = json.dumps(msg)
#print(msg)
# send string to mqtt
status = pingMQTT(name, msg2)
print("Status:", status)



