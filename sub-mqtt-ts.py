import serial
import time
import logging
import sys
import paho.mqtt.client as mqtt
import json

# Konfigurasi MQTT ThingSpeak
client_id = "PAAFExceBywqKDM1LAwzEjY"
username = "PAAFExceBywqKDM1LAwzEjY"
password = "MIGKghWjiQg0Fy0c8LFWzsjt"
pub_topic = "channels/2712512/subscribe"
broker = "mqtt3.thingspeak.com"
broker_port = 1883

# Define event callbacks for MQTT
def on_connect(client, userdata, flags, rc):
    logging.info("Connection Result: " + str(rc))
    # Kirim data sensor sebagai payload JSON melalui MQTT ke ThingSpeak
    client.subscribe(pub_topic)

def on_message(client, userdata, msg):
    print(json.loads(msg.payload)) #converting the string back to a JSON object

# Membuat client MQTT
# client = mqtt.Client(client_id)
client = mqtt.Client(client_id=client_id)
# client.username_pw_set(username, password)

# Assign event callbacks
client.on_connect = on_connect
client.on_message = on_message

# Menghubungkan ke broker MQTT ThingSpeak
client.username_pw_set(username, password)
client.connect(broker, broker_port, 60)

client.loop_forever()

