#pragma once
#include "deviceState.h"

#define PIN_RED 23
#define PIN_GREEN 22
#define PIN_BLUE 21
void setupComponentDHT();
void setupComponentLed();
struct DHTSensorReadings {
  float temperatureCelcius;
  float temperatureFahrenheit;
  float humidityPercent;
  float heatIndexCelcius;
  float heatIndexFahrenheit;
  bool isReadingsValid;
  bool hasNewReading;
  unsigned long sampledAt;
};
DHTSensorReadings handleDhtSensor();
void setLedForState(DeviceState state, bool mqttIsConnected);
