from MongoUtil import MongoUtil
from Sensor import Sensors
import json

db = "test"
col = "Observations"

# Get sensor object for data
s = Sensors()
# Get json structure of values
msg = s.get_observations()
#print(msg)
# send string to mqtt
mu = MongoUtil()
status = mu.save_many(db, col, msg)
print(status)
