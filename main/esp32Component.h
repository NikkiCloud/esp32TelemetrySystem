void handleLed(String msg);
struct DHTSensorReadings {
  float temperatureCelcius;
  float temperatureFahrenheit;
  float humidityPercent;
  float heatIndexCelcius;
  float heatIndexFahrenheit;
  bool isReadingsValid;
  unsigned long timestamp_millisec;
};
DHTSensorReadings handleDhtSensor();
