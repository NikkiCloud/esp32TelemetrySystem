#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include "secrets.h"
#include "esp32Component.h"
#include "mqtt.h"

//mqtt broker details
const char* mqtt_broker = "637cb61c1803425c8862e3564bb87c31.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;
const char* mqtt_username = MQTT_USERNAME;
const char* mqtt_pwd = MQTT_PWD;

// time variables
unsigned long currentMillis;
unsigned long mqttPreviousMillis = 0;
//mqtt topic for tests
const char* topic_publish_test = "esp32/test";
const char* topic_subscribe_test = "esp32/sub_test";
const char* topic_publish_dht_readings = "esp32/dht11_sensor";

WiFiClientSecure wifiClient;
PubSubClient mqttClient(wifiClient);

void setupMQTT(){
  wifiClient.setInsecure();
  mqttClient.setServer(mqtt_broker,mqtt_port);
  mqttClient.setCallback(mqttCallback);
}

void connectAndReconnectToBrokerMQTT(){
  if(!mqttClient.connected()){
    Serial.println("Connecting to mqtt broker... pls wait...");
    delay(2000);
    setupMQTT();
    
    if(mqttClient.connect("esp32Client", mqtt_username, mqtt_pwd)){
      Serial.println("Connected to MQTT broker");
      mqttClient.subscribe(topic_subscribe_test);
      Serial.println(String("Susbcribed to topic :" ) + topic_subscribe_test);
    }
    else {
      Serial.println(String("Connection failed... current state : ") + mqttClient.state());
      delay(2000);
    }
  }
  mqttClient.loop();
}

String structToJsonDh11Readings(){
  DHTSensorReadings dhtReadings = handleDhtSensor();
  if(!dhtReadings.isReadingsValid){
    Serial.println("DHT11 readings are invalid...");
    return "";
  }
  else {
    String json = "{";
    json += "\"temperatureCelcius\":" + String(dhtReadings.temperatureCelcius);
    json += ",\"temperatureFahrenheit\":" + String(dhtReadings.temperatureFahrenheit);
    json += ",\"humidityPercent\":" + String(dhtReadings.humidityPercent);
    json += ",\"heatIndexCelcius\":" + String(dhtReadings.heatIndexCelcius);
    json += ",\"heatIndexFahrenheit\":" + String(dhtReadings.heatIndexFahrenheit);
    json += "}";

    return json;
  }
}

void publishToBrokerMQTT(){
  connectAndReconnectToBrokerMQTT();
  currentMillis = millis();

  if(currentMillis - mqttPreviousMillis >= 10000){
    mqttPreviousMillis = currentMillis;
    //publish msg to topic
    mqttClient.publish(topic_publish_test, "Ceci est un test");
    String readingsJson = structToJsonDh11Readings();
    mqttClient.publish(topic_publish_dht_readings, readingsJson.c_str());

  }
}

void mqttCallback(const char* topic, byte* payload, unsigned int length){
    String message;
    for(int i = 0; i < length; i++){
      message += (char)payload[i];
    }
    if(String(topic) == topic_subscribe_test){
      handleLed(message);
    } 
}
