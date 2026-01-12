#pragma once
#include "esp32Component.h"
void mqttLoop();
void publishToBrokerMQTT(DHTSensorReadings dhtReadings);
void mqttCallback(const char* topic, byte* payload, unsigned int length);
bool mqttIsConnected();
void wrapperForConnectAndReconnectToBrokerMQTTFunction();
