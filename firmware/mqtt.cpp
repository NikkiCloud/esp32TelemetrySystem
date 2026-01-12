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
const unsigned long PUBLISH_INTERVAL = 5000;
unsigned long lastPublishedSampledAt = 0;

bool togglePublishTopic = false;

WiFiClientSecure wifiClient;
PubSubClient mqttClient(wifiClient);

void setupMQTT(){
  wifiClient.setInsecure();
  mqttClient.setServer(mqtt_broker,mqtt_port);
  mqttClient.setBufferSize(512);
  mqttClient.setCallback(mqttCallback);
}

void mqttLoop(){
  if(mqttClient.connected()){
    mqttClient.loop();
  }
}

void connectAndReconnectToBrokerMQTT(){
  if(!mqttClient.connected()){
    Serial.println("Connecting to mqtt broker... pls wait...");
    delay(2000);
    setupMQTT();
    
    if(mqttClient.connect("esp32Client", mqtt_username, mqtt_pwd)){
      Serial.println("Connected to MQTT broker");
    }
    else {
      Serial.println(String("Connection failed... current state : ") + mqttClient.state());
      delay(2000);
    }
  }
}

bool mqttIsConnected(){
  return mqttClient.connected();
}

void wrapperForConnectAndReconnectToBrokerMQTTFunction(){
  connectAndReconnectToBrokerMQTT();
}

String structToJsonDh11Readings(DHTSensorReadings dhtReadings, unsigned long publishedAt, bool isReadingNewComparedToLastOne, unsigned long ageReadingsMillis){
  
  String json = "{";
    json += "\"isReadingValid\":" + String(dhtReadings.isReadingsValid ? "true" : "false");
    json += ",\"hasNewReading\":" + String(isReadingNewComparedToLastOne ? "true" : "false");
    json += ",\"sampledAt\":" + String(dhtReadings.sampledAt);
    json += ",\"publishedAt\":" + String(publishedAt);
    json += ",\"ageReadings\":" + String(ageReadingsMillis);
  
  if(!dhtReadings.isReadingsValid){
    Serial.println("DHT11 readings are invalid...");
  }
  
  if(dhtReadings.isReadingsValid) {
    json += ",\"temperatureCelcius\":" + String(dhtReadings.temperatureCelcius);
    json += ",\"temperatureFahrenheit\":" + String(dhtReadings.temperatureFahrenheit);
    json += ",\"humidityPercent\":" + String(dhtReadings.humidityPercent);
    json += ",\"heatIndexCelcius\":" + String(dhtReadings.heatIndexCelcius);
    json += ",\"heatIndexFahrenheit\":" + String(dhtReadings.heatIndexFahrenheit);
  }
  else {
    json += ",\"error\":\"DHT_READ_FAILED\"";
  }
  
  json += "}";
  return json;
}

void publishToBrokerMQTT(DHTSensorReadings dhtReadings){
  connectAndReconnectToBrokerMQTT();
  currentMillis = millis();

  if(currentMillis - mqttPreviousMillis >= PUBLISH_INTERVAL){
    mqttPreviousMillis = currentMillis;
    Serial.println("Publishing to broker");
    Serial.print("MQTT connected right now? ");
    Serial.println(mqttClient.connected() ? "yes" : "no");
    Serial.print("WiFi status: ");
    Serial.println(WiFi.status());
    
    bool isReadingNewComparedToLastOne = (dhtReadings.sampledAt !=0) && (dhtReadings.sampledAt != lastPublishedSampledAt);
    unsigned long ageReadingsMillis = (dhtReadings.sampledAt == 0) ? 0 : (currentMillis - dhtReadings.sampledAt);
    
    String readingsJson = structToJsonDh11Readings(dhtReadings, currentMillis, isReadingNewComparedToLastOne, ageReadingsMillis);
    
    //publish msg to topic
    const char* topic_publish_dht_readings = togglePublishTopic ? "iot/home/A01/telemetry" : "iot/home/B01/telemetry";
    togglePublishTopic = !togglePublishTopic;
    
    if(isReadingNewComparedToLastOne){
      lastPublishedSampledAt = dhtReadings.sampledAt;
    }
  }
}

void mqttCallback(const char* topic, byte* payload, unsigned int length){
    String message;
    for(int i = 0; i < length; i++){
      message += (char)payload[i];
    } 
}
