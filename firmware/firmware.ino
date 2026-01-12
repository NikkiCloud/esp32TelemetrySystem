#include "wifiConnection.h"
#include "mqtt.h"
#include "esp32Component.h"

DHTSensorReadings lastestReadings;
enum class DeviceState{
  INIT,
  RUNNING,
  ERROR
};
DeviceState state = DeviceState::INIT;
unsigned long mqttDownSinceMillisec = 0;
const unsigned long MQTT_DOWN_MAX_ALLOWED = 20000;

void setup() {
  Serial.begin(115200);
  connectToWifi();
  setupComponentDHT();
  wrapperForConnectAndReconnectToBrokerMQTTFunction();
}

void loop() {
  switch(state){
    
    case DeviceState::INIT: {
      Serial.println("Device State : INIT");
      mqttDownSinceMillisec = 0;
      state = DeviceState::RUNNING;
      break;
    }

    case DeviceState::RUNNING :{
      Serial.println("Device State : RUNNING");
      reconnectToWifi();
      wrapperForConnectAndReconnectToBrokerMQTTFunction();
      mqttLoop();

      if(!mqttIsConnected()){
        if(mqttDownSinceMillisec == 0){
          Serial.println("MQTT down so starting timer");
          mqttDownSinceMillisec = millis();
        }
        else if(millis() - mqttDownSinceMillisec > MQTT_DOWN_MAX_ALLOWED){
          Serial.println("Error : MQTT down for too long");
          state = DeviceState::ERROR;
          break;
        }
      }
      else {
        mqttDownSinceMillisec = 0;
      }
      DHTSensorReadings readings = handleDhtSensor();
      if(readings.hasNewReading){
        lastestReadings = readings;
      }
      publishToBrokerMQTT(lastestReadings);
      break;
    }

    case DeviceState::ERROR :{
      Serial.println("Device State : ERROR");
      reconnectToWifi();
      wrapperForConnectAndReconnectToBrokerMQTTFunction();
      Serial.println("Error : MQTT down for too long");

      if(mqttIsConnected()) {
        Serial.println("Recovered MQTT Connection");
        mqttDownSinceMillisec = 0;
        state = DeviceState::RUNNING;
      }
      break;
    }
  }
}
