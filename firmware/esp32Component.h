#pragma once
#define PIN_RED 23
#define PIN_GREEN 22
#define PIN_BLUE 21
void handleLed(String msg);
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
