'''
A group of MongoDB functions to demonstrate and test query capabilities.
This generates the data needed to populate the Fairchild spreadsheet from data sources

Author: Howard Webb
Date: 6/29/2021
'''

from pymongo import MongoClient
import dns.resolver
from pprint import pprint
import json
from datetime import datetime
# not used
from bson.json_util import dumps, loads

# logon string to get into the database
url = 'mongodb+srv://webbhm:sHzHKD9_vZUGCZ4@gbe-d.cc79x.mongodb.net/test'

# Source directories for data files, not used here
DIR = "/home/pi/python/Mongo/"
pheno_file = "Pheno.csv"

class MongoUtil(object):
    
    def __init__(self):
        # Create a database client
        dns.resolver.default_resolver=dns.resolver.Resolver(configure=False)
        dns.resolver.default_resolver.nameservers=['8.8.8.8']
        self._client = MongoClient(url)

    # save activity records
    def save_many(self, db, col, rec_set):
        # save array of records to database (db) and collection (col)
        db = self._client[db]
        col = db[col]
        ret = col.insert_many(rec_set)
        pprint(ret)
        
    def find(self, query):
        return self._client.test.Activity.find(query)
    
    # Main function used to access observtion data
    def aggregate(self, query):
        return self.aggregate2('test', 'Activity', query)
    
    def aggregate2(self, db, col, query):
        return self._client[db][col].aggregate(query)    
    
    def update(self, db, col, find, update):
        return self._client[db][col].update_many(find, update)
        
            
def test2():
    '''
    Minimal record retreival
    Very boring and little value
    '''
    mu = MongoUtil()
    #recs = mu._client.test.Observations.find({subject: {attribute: {name:"Temperature"}}})
    query = {"subject.attribute.name":"Air"}
    recs = mu.find(query)
    pprint(recs)
    
def query(query):
    '''
    Wrapper for the aggregate function
    Used by most of the tests

    '''
    mu = MongoUtil()    
        
    recs = mu.aggregate(query)
    print("Recs",recs)
    #for rec in recs:
    #    pprint(rec)
    return recs        
    
#####  Fun starts below here #######


def test3():
    '''
    Start with 20 minute sensor data and the Trial record
    Aggregate the data to attribute, weekly summary
    Pivot the summary into weekly records
    Pivot the data again into a trial summary
    
    This is one of the more complex aggregates
    It is a data aggregate and double pivot
    '''

    # Get the trial record for adding key id fields to the summary    
    trial = get_trial("GBE_T1")
    #pprint(trial)
    trial_id = trial["_id"]
    start_date = trial["time"]["start_date"]
    end_date = trial["time"]["end_date"]
    
    #print("Trial", trial_id)
    #print("Start", start_date)
    #print("End", end_date)

    # Retreive the 20 minute sensor records for a trial date range
    match = {"$match":{
           "location.school":"OpenAgBloom",
           "location.field":"GBE_D_3",
           "activity_type": "Environment_Observation",           
           "status.status_qualifier":"Test",
           "time.timestamp":{"$gt":start_date},
           "time.timestamp":{"$lt":end_date},
           #"subject.attribute.name":"Temperature"
         }}
    
    # Add trial and date information to the selected records
    # Week is the only field that really matters, others were for testing
    af = {"$addFields":{
                 "time.period_type":"Week",
                 "time.start":{"$toDate":start_date},
                 "time.ts":{"$toDate":"$time.timestamp"},
                 "time.date":{"$dateToString":{"date":{"$toDate":"$time.timestamp"}, "format":"%Y-%m-%d %H:%M:%S"}},
                 "time.dif":{"$subtract":["$time.timestamp", start_date]},
                 "time.trial_day":{"$toInt":{"$add":[{"$divide":[{"$subtract":["$time.timestamp", start_date]}, 86400000]}, 1]}},
                 # Divide difference to get number of weeks
                 "time.trial_week":{"$toInt":{"$add":[{"$divide":[{"$subtract":["$time.timestamp", start_date]}, 604800000]}, 1]}}                 }}        
    
    # Group and summarize by attribute and week
    # null in avg is probably due to a bad data record
    group = {"$group":{"_id":{
        "School":"$location.school",
        "Field":"$location.field",
        "Trial":trial_id,
        "Attribute":"$subject.attribute.name",
        "Week":"$time.trial_week"
        },
        "value":{"$min":"$subject.attribute.value"},
        "min":{"$min":"$subject.attribute.value"},
        "max":{"$max":"$subject.attribute.value"},
        "avg":{"$avg":"$subject.attribute.value"},
    }}
    
    # Combine all attributes for a week together into an array
    group2 = {"$group":{"_id":{"School":"$_id.School",
                               "Field":"$_id.Field",
                               "Trial":"$_id.Trial",
                               "Week":"$_id.Week",
                               },
        "Measurments":{"$addToSet":{
            "name":"$_id.Attribute",
            "values":{
                "avg":"$avg",
                "min":"$min",
                "max":"$max",
                "value":"$value"
                }
            }}
    }}
    
    # WARNING: removes attribute form all places, not just in _id
    # This is not used but has interesting possibilities
    unset = {"$unset":[
        "_id.Attribute",
        ]}
    
    # Pivot on Attributes to form a week record
    project = {"$project":
        {"Measurments":{"$arrayToObject":{
            "$zip":{"inputs":["$Measurments.name", "$Measurments.values"]}
            }}}}
    
    # Group weeks to a trial and build a record array
    group3 = {"$group":{"_id":{"School":"$_id.School",
                               "Field":"$_id.Field",
                               "Trial":"$_id.Trial",
                               },
                               
                   "Measurments":{"$addToSet":{
                   "name":{"$concat":["Week_",{"$toString":"$_id.Week"}]},
                   "values":"$Measurments"
                   }}}
              }
    
    # Pivot on week
    project2 = {"$project":
        {"Week":{"$arrayToObject":{
            "$zip":{"inputs":["$Measurments.name", "$Measurments.values"]}
            }}}}    
       
    
    # Not used
    sort = {"$sort":{"_id.Week":1}}
    
    #q = [match]
    #q = [match, af] # add trial_id and week
    #q = [match, af, group]    
    #q = [match, af, group, unset]
    #q = [match, af, group, unset, group2]
    #q = [match, af, group, group2, project]
    #q = [match, af, group, group2, project, group3]
    q = [match, af, group, group2, project, group3, project2]            
    recs = query(q)
    #print("Type", type(recs))
    return recs
    
def get_trial(trial_id):
    '''
    Retreive the trial record
    '''
    mu = MongoUtil()
    query = {"_id":"GBE_T1"}
    recs = mu._client.test.Trial.find(query)
    #print(type(recs))
    lst = list(recs)
    #print(type(lst))
    #rec = dumps(lst)
    #print(type(lst))
    if len(lst) == 1:
        return lst[0]
    
    return None
        
def AgroPivot():
    '''
    Select phenotype records for a trial
    Group, summarize and form an array of data by attributes
    '''


    match = {"$match":{
           "location.school":"OpenAgBloom",  #note spelling error
           "location.field":"GBE_D_3",
           "trial":"GBE_T1",
           "activity_type": "Phenotype_Observation",           
           "status.status_qualifier":"Test",
           #"subject.attribute.name":"Temperature"
         }}
    
    group2 = {"$group":{"_id":{"School":"$location.school",
                              "Field":"$location.field",
                              "Plot":"$location.plot","Week":"$time.week",
                               "Trial":"$trial",
                               "Attrib":"$subject.attribute.name",
                               "GBE_Id":"$subject.GBE_Id",
                               "type":"$subject.type",
                               "Attrib":"$subject.attribute.name"},
                   "items":{"$addToSet":{    
                   "average":{"$avg":"$subject.attribute.value"},
                   "min":{"$min":"$subject.attribute.value"},
                   "max":{"$max":"$subject.attribute.value"}                   
                   }}}}
    
    group = {"$group":{"_id":{"School":"$location.school",
                              "Field":"$location.field",
                              "Plot":"$location.plot","Week":"$time.week",
                              "Trial":"$trial",
                               "Attrib":"$subject.attribute.name",
                               "GBE_Id":"$subject.GBE_Id",
                               "type":"$subject.type",
                               "Week":"$time.week",
                               "Attrib":"$subject.attribute.name"},
                   "average":{"$avg":"$subject.attribute.value"},
                   "min":{"$min":"$subject.attribute.value"},
                   "max":{"$max":"$subject.attribute.value"}                   
                   }}
                   
    sort = {"$sort":{"_id.Week":1, "_id.Attrib":1}}
    
    project = {"$project":
        {"tmp":{"$arrayToObject":{
            
            }}}}
            
    addF = {"$addFields":
            {"tmp.week":"$_id.Week",
             "tmp.attrib":"$_id.Attrib",
             "tmp.plot":"$_id.Plot"
             }}
    
    rep = {"$replaceRoot":{"newRoot":"$tmp"}}
    
    q = [match, group2]
    #q = [match, group]    
    recs = query(q)
    file_name = DIR + "AgroRpt.txt"
    save(file_name, recs)    
    
        
def PhenoPivot():
    '''
    Summarize and Pivot pheno obsv to the week and attribute
    Add dimension calculations
    Pivot to week
    '''
    # Select pheontype records for a trial
    match = {"$match":{
           "location.school":"OpenAgBloom",  #note spelling error
           "location.field":"GBE_D_3",
           "trial":"GBE_T1",
           "activity_type": "Phenotype_Observation",           
           "status.status_qualifier":"Test",
           #"subject.attribute.name":"Temperature"
         }}
    
    # Group by attribute and week, aggregate and summarize
    group = {"$group":{"_id":{"School":"$location.school",
                              "Field":"$location.field",
                              "Plot":"$location.plot",
                              "Trial":"$trial",
                              #"Attrib":"$subject.attribute.name",
                              "GBE_Id":"$subject.GBE_Id",
                              "type":"$subject.type",
                              "Week":"$time.week"},
                   "items":{"$addToSet":{
                   "name":"$subject.attribute.name",
                   "values":{
                       "Avg":{"$avg":"$subject.attribute.value"},
                       "Min":{"$min":"$subject.attribute.value"},
                       "Max":{"$max":"$subject.attribute.value"}
                       }
                   }}}}
    
    # Pivot the attributes together by week
    project = {"$project":
        {"Plant":{"$arrayToObject":{
            "$zip":{"inputs":["$items.name", "$items.values"]}
            }}}}
    
    # Add dimension and slope (rate of growth)
    af = {"$addFields":{
                 "Plant.Dimension":{"$multiply":["$Plant.Height.Avg", "$Plant.Width.Avg", "$Plant.Length.Avg"]},
                 "Plant.Slope":{"$divide":[{"$multiply":["$Plant.Height.Avg", "$Plant.Width.Avg", "$Plant.Length.Avg"]}, 28]},
                 }}    
    
    # Group and array by week
    group2 = {"$group":{"_id":{"School":"$_id.School",
                              "Field":"$_id.Field",
                              "Plot":"$_id.Plot",
                              "Trial":"$_id.Trial",
                              "Attrib":"$_id.Attrib",
                              "GBE_Id":"$_id.GBE_Id",
                              "type":"$_id.type"},
                   "Measurments":{"$addToSet":{
                   "Week":{"$toString":"$_id.Week"},
                   "values":"$Plant"
                   }}}
              }
    
    # Pivot week to the trial level
    project2 = {"$project":
        {"Week":{"$arrayToObject":{
            "$zip":{"inputs":["$Measurments.Week", "$Measurments.values"]}
            }}}}    

    
   
    sort = {"$sort":{"_id.Week":1, "_id.Plot":1}}    
    
    #q = [match]
    #q = [match, group]
    #q = [match, group, project]
    #q = [match, group, project, af]
    #q = [match, group, project, af, group2]        
    #q = [match, group, project, af, group2, project2]    
    q = [match, group, project, af, group2, project2, sort]    
    
    recs = query(q)
    #for rec in recs:
    #    pprint(rec)
    file_name = DIR + "PhenoRpt.txt"
    print(file_name)
    save(file_name, recs)    
    
def Growth_Rate():
    '''
    Summarize and Pivot growth obsv to the week and attribute
    Add dimension calculations
    Pivot to week
    '''
    # Select pheontype records for a trial
    match = {"$match":{
           "location.school":"OpenAgBloom",
           "location.field":"GBE_D_3",
           "trial":"GBE_T1",
           "activity_type": "Phenotype_Observation",           
           "status.status_qualifier":"Test",
           "subject.attribute.name":{"$in":["Height", "Length", "Width"]}
         }}
    
    # Group by attribute and week, aggregate and summarize
    group = {"$group":{"_id":{"School":"$location.school",
                              "Field":"$location.field",
                              "Plot":"$location.plot",
                              "Trial":"$trial",
                              #"Attrib":"$subject.attribute.name",
                              "GBE_Id":"$subject.GBE_Id",
                              "type":"$subject.type",
                              "Week":"$time.week"},
                   "items":{"$addToSet":{
                   "name":"$subject.attribute.name",
                   "values":{
                       "Avg":{"$avg":"$subject.attribute.value"},
                       "Min":{"$min":"$subject.attribute.value"},
                       "Max":{"$max":"$subject.attribute.value"}
                       }
                   }}}}
    
    # Pivot the attributes together by week
    project = {"$project":
        {"Plant":{"$arrayToObject":{
            "$zip":{"inputs":["$items.name", "$items.values"]}
            }}}}
    
    # Add dimension and slope (rate of growth)
    af = {"$addFields":{
                 "Plant.Dimension":{"$multiply":["$Plant.Height.Avg", "$Plant.Width.Avg", "$Plant.Length.Avg"]},
                 "Plant.Slope":{"$divide":[{"$multiply":["$Plant.Height.Avg", "$Plant.Width.Avg", "$Plant.Length.Avg"]}, 28]},
                 }}    
    
    # Group and array by week
    group2 = {"$group":{"_id":{"School":"$_id.School",
                              "Field":"$_id.Field",
                              "Plot":"$_id.Plot",
                              "Trial":"$_id.Trial",
                              "Attrib":"$_id.Attrib",
                              "GBE_Id":"$_id.GBE_Id",
                              "type":"$_id.type"},
                   "Measurments":{"$addToSet":{
                   "Week":{"$toString":"$_id.Week"},
                   "values":"$Plant"
                   }}}
              }
    
    # Pivot week to the trial level
    project2 = {"$project":
        {"Week":{"$arrayToObject":{
            "$zip":{"inputs":["$Measurments.Week", "$Measurments.values"]}
            }}}}    

    
   
    sort = {"$sort":{"_id.Week":1, "_id.Plot":1}}    
    
    #q = [match]
    #q = [match, group]
    #q = [match, group, project]
    #q = [match, group, project, af]
    #q = [match, group, project, af, group2]        
    #q = [match, group, project, af, group2, project2]    
    q = [match, group, project, af, group2, project2, sort]    
    
    recs = query(q)
    return recs    
                
def Pivot3():
    '''
    Phenotype pivoting on week and attribute
    Basically a copy of the previous function, saved as copy while making changes
    '''
    match = {"$match":{
           "location.school":"OpenAgBloom",  #note spelling error
           "location.field":"GBE_D_3",
           "trial":"GBE_T1",           
           "activity_type": "Phenotype_Observation",           
           "status.status_qualifier":"Test",
           #"subject.attribute.name":"Temperature"
         }}
    
    # Get attribute values by week
    group = {"$group":{"_id":{"School":"$location.school",
                              "Field":"$location.field",
                              "Plot":"$location.plot",
                              "Trial":"$trial",
                              "Attrib":"$subject.attribute.name",
                              "GBE_Id":"$subject.GBE_Id",
                              "type":"$subject.type",
                              "Week":"$time.week"},
                   "items":{"$addToSet":{
                   "name":"$subject.attribute.name",
                   "values":{
                       "Avg":{"$avg":"$subject.attribute.value"},
                       "Min":{"$min":"$subject.attribute.value"},
                       "Max":{"$max":"$subject.attribute.value"}
                       }
                   }}}}
    
    # 1st organization, group by week, attribute
    project = {"$project":
        {"Plant":{"$arrayToObject":{
            "$zip":{"inputs":["$items.name", "$items.values"]}
            }}}}
    

    # Add dimension and slope
    af = {"$addFields":{
                 "Plant.Dimension":{"$multiply":["$Plant.Height.Avg", "$Plant.Width.Avg", "$Plant.Length.Avg"]},
                 "Plant.Slope":{"$divide":[{"$multiply":["$Plant.Height.Avg", "$Plant.Width.Avg", "$Plant.Length.Avg"]}, 28]},
                 }}

    # Group by week
    group2 = {"$group":{"_id":{"School":"$_id.School",
                              "Field":"$_id.Field",
                              "Plot":"$_id.Plot",
                              "Trial":"$_id.Trial",
                              "Attrib":"$_id.Attrib",
                              "GBE_Id":"$_id.GBE_Id",
                              "type":"$_id.type"},

                   "items":{"$addToSet":{
                   "Week":"$_id.Week",
                   "values":"$Plant"
                       
                   }}}}
    
    project2 = {"$project":
        {"Plant":{"$arrayToObject":{
            "$zip":{"inputs":["$items.Week", "$items.values"]}
            }}}}    
   
    sort = {"$sort":{"_id.Week":1, "_id.Plot":1}}    
    
    #q = [match, group]
    #q = [match, group, project]
    #q = [match, group, project, af]
    q = [match, group, project, af, group2]
    #q = [match, group, project, af, group2, project2]
    #q = [match, group, project, af, group2, project2, sort]        
    recs = query(q)
    for rec in recs:
        pprint(rec)
    file_name = DIR + "PhenoRpt.txt"
    save(file_name, recs)        
    print("Done")
    
def Planting():
    '''
    Summarize and aggregaate agronomic data to the week and trial
    Get number of plants planted and planting date
    '''
    # Get agronomic activity for trial
    match = {"$match":{
           "location.school":"OpenAgBloom",  #note spelling error
           "location.field":"GBE_D_3",
           "trial":"GBE_T1",
           "activity_type": "Agronomic_Activity",           
           "status.status_qualifier":"Test",
           "subject.attribute.name":"Planting",
           #"subject.attribute.name":"Temperature"
         }}
    
    # group by attribute, add first planting data and total seeds planted
    group = {"$group":{"_id":{"School":"$location.school",
                              "Field":"$location.field",
                              "Plot":"$location.plot",
                              "Trial":"$trial",
                              "Attrib":"$subject.attribute.name",
                              "GBE_Id":"$subject.GBE_Id",
                              "type":"$subject.type"},
                #"time.planting_date_str":{"$dateToString":{"format":"%Y-%m-%d %H:%M:%S", "date":{"$first":"$time.timestamp"}}},
                "planting_date":{"$first":"$time.timestamp"},                       
                "seeds_planted":{"$sum":"$subject.attribute.value"},
                   }}
    
    sort2 = {"$sort":{"_id.Plot":1}}        
            
    q = [match, group, sort2]    
    recs = query(q)
    return recs
    #file_name = DIR + "PlantingRpt.txt"
    #save(file_name, recs)    
    
def Germination():
    '''
    Get first germination data and total number germinated
    Could probably combine this with planting by getting all attributes and pivoting
    '''
    
    match = {"$match":{
           "location.school":"OpenAgBloom",  #note spelling error
           "location.field":"GBE_D_3",
           "trial":"GBE_T1",
           "activity_type": "Agronomic_Activity",           
           "status.status_qualifier":"Test",
           "subject.attribute.name":"Germination",
           #"subject.attribute.name":"Temperature"
         }}
    
    addF = {"$addFields":
            {"plot.id":"$location.plot",
             "plot.plant.name":"$subject.type",
             "plot.plant.id":"$subject.GBE_Id",
             "plot.time":"$time",
             }}
    
    
    sort = {"$sort":{"time.day":1}}    
    # group by plot
    group = {"$group":{"_id":{"School":"$location.school",
                              "Field":"$location.field",
                              "Plot":"$location.plot",
                              "Trial":"$trial",
                              "Attrib":"$subject.attribute.name",
                              #"GBE_Id":"$subject.GBE_Id",
                              #"type":"$_id.type"
                              },
                "plot":{"$first":"$plot"},
                #"time":{"$first":"$time"},
                #"first_germination_date_str":{"$dateToString":{"format":"%Y-%m-%d %H:%M:%S", "date":{"$first":"$time.timestamp"}}},                       
                "total_seeds_germinated":{"$sum":"$subject.attribute.value"},
                   }}
    # put count inside plot
    addF2 = {"$addFields":
            {"plot.germinated":"$total_seeds_germinated",
             }}
    


    unset = {"$unset":[
        "total_seeds_germinated",
        ]}    
    
    sort2 = {"$sort":{"_id.Plot":1}}        
            
    #q = [match]
    #q = [match, sort, group]
    #q = [match, sort, addF, group]
    #q = [match, sort, addF, group, addF2, unset]
    q = [match, sort, addF, group, addF2, unset, sort2]            
    recs = query(q)
    #file_name = DIR + "GermRpt.txt"
    #for rec in recs:
    #    pprint(rec)
    #save(file_name, recs)
    return recs
    
def lookup():
    # Join between two tables observation and trial
    match = {"$match":{
           "location.school":"OpenAgBloom",  #note spelling error
           "location.field":"GBE_D_3",
           "trial":"GBE_T1",           
           "activity_type": "Phenotype_Observation",           
           "status.status_qualifier":"Test",
           #"subject.attribute.name":"Temperature"
         }}

    lookup = {"$lookup":{
                "from":"Trial",
                "localField":"trial",
                "foreignField":"activity.id",
                "as":"Foo"
                }
                }
                
    q = [match, lookup]    
    query(q)
    
def ObsvByPerson():
    # Count of observations made by each student for the trial
    # sorted most to least
    match = {"$match":{
           "location.school":"OpenAgBloom",
           "location.field":"GBE_D_3",
           "trial":"GBE_T1",
           "status.status_qualifier":"Test",
           "participant.type":"person",
         }}
    
    group = {"$group":{"_id":{"School":"$location.school",
                              "Field":"$location.field",
                              "Trial":"$trial",
                              "Student":"$participant.name"
                              },
                "count":{"$sum":1},
                   }}
    
    sort = {"$sort":{"count":-1}}        

    q = [match, group, sort]    
    recs = query(q)
    file_name = DIR + "StudentObsvRpt.txt"
    save(file_name, recs)    
    
def testEnvSummary():
    '''
    High level wrapper for the Environment function
    '''
    trial_id = "GBE_T1"
    recs = get_trial(trial_id)
    #for rec in recs:
    #    pprint(rec)
    recs = test3()
    #for rec in recs:
    #   pprint(rec)
    file_name = DIR + "EnvRpt.txt"
    save(file_name, recs)
    print("Done")
    
def testTrial():
    # retreive the trial record and use it for testing date functions
    match = {"$match":{
           "location.school.name":"OpenAgBloom",
           "location.field":"GBE_D_3",
           "activity.id":"GBE_T1"
         }}
    
    # Add week
    af = {"$addFields":{
                 "time.period_type":"Week",
                 # simply get the number
                 "time.start":"$time.start_date",
                 # convert number to date object
                 "time.st_dt":{"$toDate":"$time.start_date"},
                 # convert date to string to see if looks right
                 "time.date":{"$dateToString":{"date":{"$toDate":"$time.start_date"}, "format":"%Y-%m-%d %H:%M:%S"}},
                 # try subtracting two numbers
                 "time.dif":{"$subtract":["$time.end_date", "$time.start_date"]},
                 # Divide difference to get number of days
                 "time.days":{"$toInt":{"$add":[{"$divide":[{"$subtract":["$time.end_date", "$time.start_date"]}, 86400000]}, 1]}},
                 # Divide difference to get number of weeks
                 "time.weeks":{"$toInt":{"$add":[{"$divide":[{"$subtract":["$time.end_date", "$time.start_date"]}, 604800000]}, 1]}}
                 }}      

    query = [match, af]
    
    recs = Trial_aggregate(query)
    for rec in recs:
        pprint(rec)
    print("Done")
    
def save(file, recs):
    f = open(file, "w")
    for rec in recs:
        pprint(rec)
        f.write(json.dumps(rec)+"\n")
    f.close()
    print("Done")
    
def update():
    db = "test"
    col = "Observations"
    # Change Environmental_Observtion to Environment_Observation
    #find = {"activity":"Environmental_Observation"}
    #update = {"$set":{"activity":"Environment_Observation"}}
    
    # Change name activity to activity_type
    find = {"activity":"Environment_Observation"}
    update = {"$rename":{"activity":"activity_type"}}
    
    # Add attribute name to attribute
    #find = {"subject.Temperature":{"$exists":"true"}}
    #update = {"$set":{"subject.Temperature.name":"Temperature"}}
    
    #find = {"subject.Pressure":{"$exists":"true"}}
    #update = {"$set":{"subject.Pressure.name":"Pressure"}}
    
    #find = {"subject.Humidity":{"$exists":"true"}}
    #update = {"$set":{"subject.Humidity.name":"Humidity"}}
    
    # rename attribute
    
    #find = {"subject.Humidity":{"$exists":"true"}}
    #update = {"$rename":{"subject.Humidity":"subject.attribute"}}
    
    #find = {"subject.Pressure":{"$exists":"true"}}
    #update = {"$rename":{"subject.Pressure":"subject.attribute"}}
    

    mu = MongoUtil()    
    status = mu.update(db, col, find, update)
    print("Update",status)
    
def planting_test():
    print("Planting Test")
    recs = Planting()
    for rec in recs:
        pprint(rec)
    #file_name = DIR + "PlantingRpt.txt"
    #save(file_name, recs)
    print("Done")

def Growth_Rate_Test():
    print("Growth Rate Test")
    recs = Growth_Rate()
    for rec in recs:
        pprint(rec)
    #file_name = DIR + "PlantingRpt.txt"
    #save(file_name, recs)
    print("Done")
    
def germ_test():
    print("Germination Test")
    recs = Germination()
    for rec in recs:
        pprint(rec)
    #file_name = DIR + "PlantingRpt.txt"
    #save(file_name, recs)
    print("Done")        
    
if __name__=="__main__":
    #testEnvSummary()
    #testTrial()
    #AgroPivot()
    #PhenoPivot()
    #ObsvByPerson()
    #germ_test()
    #planting_test()
    #test2()
    #update()
    Growth_Rate_Test()
    print("Finished")