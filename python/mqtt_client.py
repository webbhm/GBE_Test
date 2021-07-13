import paho.mqtt.client as mqtt
import io
import json

#from set40On import set40On
#from set40Off import set40Off


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("OpenAgBloom/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
#    print type(msg.payload)
#    print len(msg.payload)
    print( msg.topic)
#    print(msg.topic+" "+str(msg.payload))
    if msg.topic == 'OpenAgBloom/byte':
        ba=bytearray(msg.payload)
        st = list(ba)
#        print st
        print( "Size: ", len(ba))
    else:
        print( msg.payload)

print("Create Client")
client = mqtt.Client()
print("Initialize connect and message")
client.on_connect = on_connect
client.on_message = on_message

print("Connect mosquitto")
client.connect("test.mosquitto.org", 1883, 60)
#client.connect("mqtt.eclipse.org", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
print("Start loop")
client.loop_forever()
