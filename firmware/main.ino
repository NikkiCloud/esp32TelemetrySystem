#include "wifiConnection.h"
#include "mqtt.h"

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  connectToWifi();
}

void loop() {
  // put your main code here, to run repeatedly:
  reconnectToWifi();
  publishToBrokerMQTT();
}
