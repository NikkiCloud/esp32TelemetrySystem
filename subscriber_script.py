import paho.mqtt.client as mqtt
import config

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
    else:
        print("Connection failed with code " + str(rc))


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed successfully, QoS: ", granted_qos)

def on_message(client, userdata, msg):
    print("Message came from topic: "+ msg.topic + ", QoS: " + str(msg.qos) + ", Message content: " + msg.payload.decode())

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