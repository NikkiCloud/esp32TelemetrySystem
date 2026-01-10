#include "wifiConnection.h"
#include "mqtt.h"
#include "esp32Component.h"
DHTSensorReadings lastestReadings;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  connectToWifi();
  setupComponentDHT();
}

void loop() {
  // put your main code here, to run repeatedly:
  reconnectToWifi();
  mqttLoop();
  DHTSensorReadings readings = handleDhtSensor();
  if(readings.hasNewReading){
    lastestReadings = readings;
  }
  publishToBrokerMQTT(lastestReadings);
}
