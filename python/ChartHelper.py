'''
# Author: Howard Webb
# Data: 7/12/2021
Data retreiver for various charts
Handles the MongoDB queries
'''

#import pygal
import requests
# python3 -m pip install --user numpy pandas
#import pandas as pd
'''
Helper file to get data for temperature charting
'''

import json
from datetime import datetime, time
import math
#from LogUtil import Logger
from MongoUtil import MongoUtil

DB = "test"
COL = "Observations"
TEMPERATURE = "Temperature"
HUMIDITY = "Humidity"
PRESSURE = "Pressure"
CO2 = "CO2"

class ChartHelper(object):
    
   
    def __init__(self, attribute):
        self._farm = None
        self._field = None
        self._trial = None
        self._attribute = attribute
        self._start_date = 0
        self.get_trial()
    

    def get_data(self):
        '''
        Run Mongo to get data
        '''
        match = {"$match":{
           "location.farm":self._farm,
           "location.field":self._field,
           "activity_type": "Environment_Observation",           
           "status.status_qualifier":"Success",
           "time.timestamp":{"$gt":self._start_date},
           "subject.attribute.name":self._attribute
         }}
        #print(match)
        query = [match]
        
        mu = MongoUtil()    
        recs = mu.aggregate2(DB, COL, query) 
        return recs
    
    def json_to_array(self, recs):
        data = {}
        date = []
        value = []
        for rec in recs:
            ts = rec["time"]["timestamp"]
            date.append(ts)
            v = rec["subject"]["attribute"]["value"]
            value.append(v)
            #print(ts, v)

            
        data["date"] = date
        data["value"] = value
        data["title"] = self._attribute
        data["farm"] = self._farm
        data["field"] = self._field
        return data
            
        
    
    def get_trial(self):
        from trial import trial
        self._farm = trial["location"]["farm"]
        self._field = trial["location"]["field"]
        self._trial = trial["name"]
        # multiply for MongoDB milliseconds
        self._start_date = int(trial["time"]["start_date"]) * 1000
        #self._subject = "Air"
        #self._attribute = "Temperature"
        #self._label = "Temperature"
        #self._units = "C"
        #self._file_name = "/home/pi/python/static/temp_chart.svg"
        
    def get_array(self):
        recs = self.get_data()
        data = self.json_to_array(recs)
        return data

def test():
    ''' Function to test the chart building with test flag set to True
           Args:
               None:
           Returns:
               None:
           Raises:
               None
    '''
    print("Temp Chart Test")    
    tc = ChartHelper()
    recs = tc.get_data(TEMPERATURE)
    #print("Recs", recs)
    #for rec in recs:
    #    print(rec)
    data = tc.json_to_array(TEMPERATURE, recs)
    print("Rec cnt", len(data["date"]))    
    #print(data)
    #build_chart(recs)

    
    print("Done")
    
def test2():
    attribute = HUMIDITY
    print("Test Data:", attribute)
    tc = ChartHelper(attribute)
    array = tc.get_array()
    print("Rec cnt", len(array["date"]))    
    print("Done")
    
        

if __name__=="__main__":
    test2()

