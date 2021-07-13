'''
Get Sensor Values
Pack into json structure
Author: Howard Webb
Date: 7/9/2021
'''

from datetime import datetime
from copy import deepcopy
from pprint import pprint

sensor_list = [{"name":"BME280", "function":{
    "module":"BME280", "class":"BME280"
    },
                "values":[
                    {"func":"getTemp", "subject":"Air", "attribute":"Temperature", "units":"C", "fmt":"{:1.1f}"},
                    {"func":"getPressure", "subject":"Air", "attribute":"Pressure", "units":"mbar", "fmt":"{:1.1f}"},
                    {"func":"getHumidity", "subject":"Air", "attribute":"Humidity", "units":"%", "fmt":"{:1.1f}"}
                    ]},
{"name":"NDIR", "function":{
    "module":"NDIR", "class":"NDIR"
    },
                "values":[
                    {"func":"getCO2", "subject":"Air", "attribute":"CO2", "units":"ppm", "fmt":"{:1.1f}"}
                    ]}
            ]


class Sensors(object):

    def __init__(self):
        """Record optional sensor data
        Args:
            lvl: Logging level
        Returns:
            None
        Raises:
            None
        """        
        self.test = False
        self._id = 'GBE-D_3'
        # timestamp as string
        self._ts_str = ''
        # timestamp as unix number
        self._timestamp = 0
        # if trial running, get day of trial
        self._trial_day = 0
        # if trial running, get week of trial
        self._trial_week = 0
        self._farm = None
        self._field = None
        self._start_date_str = ''
        self_start_date = 0
        self._trial_id = None
        # load trial info
        self.get_trial()
        self.get_time()
        
    def get_trial(self):
        '''
        Get trial data from trial.py
        '''
        from trial import trial
        self._trial_id = trial["name"]
        self._start_date = datetime.fromtimestamp(trial['time']['start_date'])
        self._start_date_str = trial['time']['start_date_str']
        self._farm = trial["location"]["farm"]
        self._field = trial["location"]["field"]
        self._status = trial["status"]["status"]
        
    def get_time(self):
        '''get time parts'''
        # convert to miliseconds for Mongo
        ts = datetime.now()
        self._timestamp = ts.timestamp() * 1000
        self._ts_str = format(ts, '%Y-%m-%d %H:%M:%S')
        if self._status == "In Process":
            lapse = ts - self._start_date
            self._trial_day = lapse.days
            self._trial_week = int(self._trial_day/7) + 1
        
        
    def get_full(self):
        # Get all sensor readings from dictionary structure
        msg = self.get_msg_body()
        #print("Msg", msg)
        sensors = {}
        for sensor in sensor_list:
            attr = self.get_attributes(sensor)
            sensors[sensor["name"]] = attr
        msg["sensors"] = sensors
        return msg
    
    
    def log(self):
        # Log Environmental Observations to persistence
        obsv = self.get_observations()
        self.persist(obsv)
        
    def get_observations(self):        
        # get a set of observations
        obsv = []
        for sensor in sensor_list:
            # Create generic observation header
            msg = self.build_obs_header()
            #print(msg)
            participant = {"type":"device", "name":sensor["name"]}
            msg["participant"] = participant
            status = {"status_qualifier":"Success"}
            msg["status"] = status
            # get all attributes for sensor
            attr = self.get_attributes(sensor)
            # break up attributes and make a separate observation for each
            for attribute in attr:
                #print(attribute)
                msg2 = deepcopy(msg)
                subject = {"name":"Air"}
                subject["attribute"] = attr[attribute]
                #print("\nSubject", subject)
                msg2["subject"] = subject
                #print("\nMsg", msg2)
                # build set of observations
                obsv.append(msg2)
        return obsv                
            
                
    def build_obs_header(self):
        # Environemntal_Observation record header
        msg = self.get_msg_body()
        msg["activity_type"] = "Environment_Observation"
        return msg
                
    def persist(self, msg):
        # Save to MongoDB - dummy for now
        print("Persist", msg)
        
        
    def get_msg_body(self):
        # Get standard header info for message
        msg = {}
        location = {"farm":self._farm, "field":self._field}
        msg["location"] = location
        time = {"timestamp":self._timestamp, "timestamp_str":self._ts_str, "trial_day":self._trial_day, "trial_week":self._trial_week}
        msg["time"] = time
        
        return msg
        
    def get_attributes(self, sensor):
        # get values for a sensor
        att = {}
        #print(senso)
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
            att[attribute] = {"name":attribute ,"value":value, "unit":unit}
        return att

                        
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
    #print(sensor_list)
    lg = Sensors()
    print("TS", lg._timestamp)
    print("Start", lg._start_date)
    print("Day", lg._trial_day)
    print("Week", lg._trial_week)
    lg.test = False
    msg = lg.get_full()
    print(msg)
    
def test2():
    print("Test Logging")
    s = Sensors()
    s.log()
    print("Done")
    
def test3():
    print("Test Logging")
    s = Sensors()
    recs = s.get_observations()
    for rec in recs:
        pprint(rec)
    print("Done")    
    
if __name__ == "__main__":
    test3()
    
