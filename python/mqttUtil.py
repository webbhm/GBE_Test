# Author: Howard Webb
# Data: 7/25/2017
# Sent temp chart via mqtt message

import paho.mqtt.client as mqtt
from datetime import datetime

def on_connect(client, userdata, flags, rc):
#    print("Connected with result code "+str(rc))
    pass

def pingMQTT(name, msg):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect("test.mosquitto.org", 1883, 60)
#    client.connect("iot.eclipse.org", 1883, 60)    
    topic='OpenAgBloom/' + name
    print( "Topic: ", topic)
    status = client.publish(topic, msg)
    client.disconnect()
    return status

def pingChart():
    timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.utcnow())
    print( "%s - tmpChart to MQTT" %timestamp)
    try:
        f=open("/home/pi/MVP/web/temp_chart.svg", "rb")
        fc=f.read()
        byteArr=bytearray(fc)
        status = pingMQTT('chart', byteArr)
        print("Pinged mqtt")
        return status
    except IOError as e:
        print("Failure to get chart")

def pingPic(pic):
    timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.utcnow())
    print( "%s - pic to MQTT" %timestamp)
    try:
        f=open(pic)
        fc=f.read()
        byteArr=bytes(fc)
        print( "Size: ", len(byteArr))
        pingMQTT('pic', byteArr)
        print("Pinged mqtt")
    except IOError as e:
        print("Failure to get image")

def pingHello():
    status = pingMQTT('hello', 'Hello World')
    return status

def pingArray():
    element=[1, 2, 3, 4, 5, 6]
    ba=bytearray(element)
    pingMQTT('byte', ba )
    print( element)

def pingExpand():
    element=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    foo=element
    for x in range(1, 20):
        foo= foo + foo
        print( len(foo))
        pingMQTT('byte', bytearray(foo))

def test():
#    pingChart()
    #pingPic("/home/pi/MVP/web/SmallImg.png")
    #pingPic("/home/pi/Pictures/gh_ph_chart.png")    
    #pingArray()
    status = pingHello()
    print("Status:", status)

if __name__=="__main__":
    test()
