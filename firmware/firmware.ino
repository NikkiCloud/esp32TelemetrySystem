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
  setupComponentLed();
  wrapperForConnectAndReconnectToBrokerMQTTFunction();
}

void loop() {
  switch(state){
    
    case DeviceState::INIT: {
      Serial.println("Device State : INIT");
      digitalWrite(PIN_BLUE, HIGH);
      digitalWrite(PIN_GREEN, LOW);
      digitalWrite(PIN_RED, LOW);
      mqttDownSinceMillisec = 0;
      Serial.println("Device State : RUNNING");
      state = DeviceState::RUNNING;
      break;
    }

    case DeviceState::RUNNING :{
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
        digitalWrite(PIN_GREEN, HIGH);
        digitalWrite(PIN_BLUE, HIGH);
        digitalWrite(PIN_RED, HIGH);
      }
      else {
        mqttDownSinceMillisec = 0;
        digitalWrite(PIN_GREEN, HIGH);
        digitalWrite(PIN_BLUE, LOW);
        digitalWrite(PIN_RED, LOW);
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
      digitalWrite(PIN_GREEN, LOW);
      digitalWrite(PIN_BLUE, LOW);
      digitalWrite(PIN_RED, HIGH);
      reconnectToWifi();
      wrapperForConnectAndReconnectToBrokerMQTTFunction();

      if(mqttIsConnected()) {
        Serial.println("Recovered MQTT Connection");
        mqttDownSinceMillisec = 0;
        state = DeviceState::RUNNING;
      }
      break;
    }
  }
}
