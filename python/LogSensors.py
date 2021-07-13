'''
Log Sensors to CSV file
Called from /home/pi/scripts/LogSensors.sh - needs to be uncommented for to run
Author: Howard Webb
Date: 9/28/2020
'''

from CSV_Util import CSV_Util
from datetime import datetime

env_header = ['type', 'site_id', 'timestamp','subject', 'attribute', 'value', 'units', 'status', 'status_qualifier', 'comment']
env_file_name = "Data.csv"

sensor_list = [{"name":"BME280", "function":{
    "module":"BME280", "class":"BME280"
    },
                "values":[
                    {"func":"getTemp", "subject":"Air", "attribute":"Temperature", "units":"C", "fmt":"{:1.1f}"},
                    {"func":"getPressure", "subject":"Air", "attribute":"Pressure", "units":"mbar", "fmt":"{:1.1f}"},
                    {"func":"getHumidity", "subject":"Air", "attribute":"Humidity", "units":"%", "fmt":"{:1.1f}"}
                    ]}]


class LogSensors(object):

    def __init__(self, file=env_file_name, header=env_header):
        """Record optional sensor data
        Args:
            lvl: Logging level
        Returns:
            None
        Raises:
            None
        """        
        self._activity_type = "Environment_Observation"
        self._persist = CSV_Util(file, header)
        self.test = False
        self._id = 'GBE-D_3'
        self._ts = format(datetime.now(), '%Y-%m-%d %H:%M:%S')
        
    def log(self):
        # Get sensor readings from dictionary structure
        for sensor in sensor_list:
            # get each sensor in the list
            #print(sensor)
            name = sensor["name"]
            module_name = sensor["function"]["module"]
            obj = sensor["function"]["class"]
            module = __import__(module_name)
            class_ = getattr(module, obj)
            instance = class_()
            for item in sensor["values"]:
                #print(item)
                #get each attribute of the sensor
                status_qualifier = "Test"
                comment = ""
                attribute = item["attribute"]
                subject = item["subject"]
                fmt = item["fmt"]
                unit = item["units"]
                # get function and call it
                value = getattr(instance, item["func"])()

                rec = ['Environment_Observation', self._id, self._ts,subject, attribute, value, unit, name, status_qualifier, comment]            
                print(rec)
                self._persist.save(rec)
        
def main():
    '''
        Function that should get called from scripts
    '''

    lg = LogSensors(env_file_name, env_header, Logger.INFO)
    lg.log()

def validate():
    '''
        Quick test to check working properly
    '''
    
    lg = LogSensors(env_file_name, env_header)
    lg.log()
    
def test():
    '''
        Use for debugging when need detailed output
    '''
    print(sensor_list)
    lg = LogSensors(env_file_name, env_header)
    lg.test = False
    lg.log()
    
if __name__ == "__main__":
    test()
    
