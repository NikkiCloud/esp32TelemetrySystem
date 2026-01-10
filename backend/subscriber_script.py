import paho.mqtt.client as mqtt
import config
import json
import time
import datetime

last_seen = {}
status = {}
OFFLINE_TIMEOUT_SEC = 30  

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
    else:
        print("Connection failed with code " + str(rc))


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed successfully, QoS: ", granted_qos)

def on_message(client, userdata, msg):
    data_dict = {}
    sensor_id = msg.topic.split("/")[2] 
    print("Sensor id: " + sensor_id + ", Message topic: "+ msg.topic + ", QoS: " + str(msg.qos) + ", Message content: " + msg.payload.decode())
    data_dict["sensor_id"] = sensor_id
    data_dict.update(convert_jsonstrin_to_dict(msg.payload))
    data_dict["received_at"] =  time.time()
    #data_dict["received_at"] =  datetime.datetime.now().isoformat()
    data_dict["topic"] =  msg.topic
    if data_dict:
        save_data_to_jsonfile(data_dict, "data/data.jsonl")
    
    now = time.time()
    last_seen[sensor_id] = now
    if status.get(sensor_id) == "OFFLINE":
        print(f"Sensor {sensor_id} is back ONLINE")
    status[sensor_id] = "ONLINE"

def convert_jsonstrin_to_dict(payload : bytes) -> dict:
    payload_str = payload.decode()
    payload_dict = json.loads(payload_str)
    return payload_dict

def save_data_to_jsonfile(data: dict, filename: str) -> None:
    with open(filename, "a") as f:
        f.write(json.dumps(data) + "\n")

def check_offline_sensors():
    now = time.time()
    for sensor_id, last_time in last_seen.items():
        if now - last_time > OFFLINE_TIMEOUT_SEC:
            if status.get(sensor_id) != "OFFLINE":
                print(f"Sensor {sensor_id} is OFFLINE")
            status[sensor_id] = "OFFLINE"

client = mqtt.Client()
client.on_connect = on_connect
client.tls_set()
client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)
client.connect(config.MQTT_BROKER, config.MQTT_PORT)
client.on_subscribe = on_subscribe
client.on_message = on_message
client.subscribe("iot/home/+/telemetry",qos=0)
client.loop_start()
while True:
    check_offline_sensors()
    time.sleep(2)
    