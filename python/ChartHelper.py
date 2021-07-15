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
from pprint import pprint

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
    
   
    def __init__(self, attribute=None):
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
    
    def get_multi_data(self, attributes):
        '''
        Run Mongo to get multiple attributes in one query
        Pivot records
        attributes should be a set of attribute names
        '''
        match = {"$match":{
           "location.farm":self._farm,
           "location.field":self._field,
           "activity_type": "Environment_Observation",           
           "status.status_qualifier":"Success",
           "time.timestamp":{"$gt":self._start_date},
           "subject.attribute.name":{"$in":attributes}
        }}
        
        # Combine all attributes for a day together into an array
        group = {"$group":{"_id":{"Farm":"$location.farm",
                               "Field":"$location.field",
                               "Time":"$time.timestamp",
                               },
        "Measurments":{"$addToSet":{
            "name":"$subject.attribute.name",
            "value":"$subject.attribute.value"
            }}
        }}        
        # pivot to attribute    
        project = {"$project":
            {"Measurments":{"$arrayToObject":{
                "$zip":{"inputs":["$Measurments.name", "$Measurments.value"]}
                }}}}      
        #print(match)
        query = [match, group, project]
        
        mu = MongoUtil()    
        recs = mu.aggregate2(DB, COL, query) 
        return recs
    
    def get_dewpoint_array(self):
        attrs = ["Temperature", "Humidity"]
        recs = self.get_multi_data(attrs)
        data = self.dewpoint_array(recs)
        return data
    
    def dewpoint_array(self, recs):
        from DewPoint import getDewPoint
        data = {}
        date = []
        t = []
        h = []
        d = []
        for rec in recs:
            try:
                #pprint(rec)
                ts = rec["_id"]["Time"]
                date.append(ts)
                temp = rec["Measurments"]["Temperature"]
                t.append(temp)
                hum = rec["Measurments"]["Humidity"]
                h.append(hum)
                dewpoint = getDewPoint(temp, hum)
                d.append(round(dewpoint, 2))
                #print(ts, temp, hum, dewpoint)
            except Exception as e:
                print(e)
            

            
        data["date"] = date
        data["temperature"] = t
        data["humidity"] = h
        data["dewpoint"] = d
        data["title"] = "Dewpoint"
        data["farm"] = self._farm
        data["field"] = self._field
        return data
    
    def get_vpd_array(self):
        # build vapor pressure deficite data for chart
        attrs = ["Temperature", "Humidity"]
        recs = self.get_multi_data(attrs)
        data = self.vpd_array(recs)
        return data        
        
    def vpd_array(self, recs):
        # convert json to array
        from VaporPressure import main
        data = {}
        date = []
        t = []
        h = []
        v = []
        for rec in recs:
            try:
                #pprint(rec)
                ts = rec["_id"]["Time"]
                date.append(ts)
                temp = rec["Measurments"]["Temperature"]
                t.append(temp)
                hum = rec["Measurments"]["Humidity"]
                h.append(hum)
                svp, avp, vpd = main(temp, hum)
                v.append(round(vpd, 2))
                #print(ts, temp, hum, dewpoint)
            except Exception as e:
                print(e)
            
        data["date"] = date
        data["temperature"] = t
        data["humidity"] = h
        data["vpd"] = v
        data["title"] = "Vapor Pressure Deficite"
        data["farm"] = self._farm
        data["field"] = self._field
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
    
def test3():
    
    attributes = ["Temperature", "Humidity"]
    print("Test Multi Data:", attributes)
    tc = ChartHelper()
    recs = tc.get_multi_data(attributes)
    #for rec in recs:
    #    pprint(rec)
    print("\nMake array")
    array = tc.dewpoint_array(recs)
    print(array)
    #print("Rec cnt", len(array["date"]))    
    print("Done")    
    
def test4():
    # dewpoint call 
    
    print("Test Dewpoint Data:")
    tc = ChartHelper()
    array = tc.get_dewpoint_array()
    print(array)
    #print("Rec cnt", len(array["date"]))    
    print("Done")
    
def test5():
    # vpd call 
    
    print("Test VPD Data:")
    tc = ChartHelper()
    array = tc.get_vpd_array()
    print(array)
    #print("Rec cnt", len(array["date"]))    
    print("Done")    


if __name__=="__main__":
    test5()

