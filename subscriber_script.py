import paho.mqtt.client as mqtt
import config
import json
import time
import datetime

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
    else:
        print("Connection failed with code " + str(rc))


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed successfully, QoS: ", granted_qos)

def on_message(client, userdata, msg):
    print("Message came from topic: "+ msg.topic + ", QoS: " + str(msg.qos) + ", Message content: " + msg.payload.decode())
    data_dict = convert_jsonstrin_to_dict(msg.payload)
    data_dict["received at"] =  time.time()
    #data_dict["received at"] =  datetime.datetime.now().isoformat()
    data_dict["topic"] =  msg.topic
    if data_dict:
        save_data_to_jsonfile(data_dict, "data.jsonl")

def convert_jsonstrin_to_dict(payload : bytes) -> dict:
    payload_str = payload.decode()
    payload_dict = json.loads(payload_str)
    return payload_dict

def save_data_to_jsonfile(data: dict, filename: str) -> None:
    with open(filename, "a") as f:
        json.dump(data, f, indent=4)

    

client = mqtt.Client()
client.on_connect = on_connect
client.tls_set()
client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)
client.connect(config.MQTT_BROKER, config.MQTT_PORT)
client.on_subscribe = on_subscribe
client.on_message = on_message
client.subscribe("esp32/dht11_sensor",qos=0)
client.loop_start()
while True:
    pass