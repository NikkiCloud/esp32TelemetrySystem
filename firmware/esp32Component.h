#pragma once
void handleLed(String msg);
void setupComponentDHT();
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
