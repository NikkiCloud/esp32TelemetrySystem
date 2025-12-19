#include <Arduino.h>
#include <DHT.h>
bool ledState = LOW;
const int DHTPIN = 4;
const int DHTTYPE = DHT11;
DHT dht(DHTPIN, DHTTYPE);
unsigned long dhtPreviousMillis = 0;
const unsigned long INTERVAL = 2000;

struct DHTSensorReadings {
  float temperatureCelcius;
  float temperatureFahrenheit;
  float humidityPercent;
  float heatIndexCelcius;
  float heatIndexFahrenheit;
  bool isReadingsValid;
  unsigned long timestamp_millisec;
};


void setupComponentLed(){
  pinMode(LED_BUILTIN, OUTPUT);
}
void setupComponentDHT(){
  dht.begin();
}

DHTSensorReadings handleDhtSensor(){
  DHTSensorReadings readings;
  setupComponentDHT();
  unsigned long currentMillis = millis();
  if(currentMillis - dhtPreviousMillis >= INTERVAL){
    dhtPreviousMillis = currentMillis;

    //code below is adapted from "https://randomnerdtutorials.com/esp32-dht11-dht22-temperature-humidity-sensor-arduino-ide/"
    // Reading temperature or humidity takes about 250 milliseconds!
    // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
    readings.humidityPercent = dht.readHumidity();
    // Read temperature as Celsius (the default)
    readings.temperatureCelcius = dht.readTemperature();
    // Read temperature as Fahrenheit (isFahrenheit = true)
    readings.temperatureFahrenheit = dht.readTemperature(true);
    // add timestamp
    readings.timestamp_millisec = millis();
  
    // Check if any reads failed and exit early (to try again).
    if (isnan(readings.humidityPercent) || isnan(readings.temperatureCelcius) || isnan(readings.temperatureFahrenheit)) {
      Serial.println(F("Failed to read from DHT sensor!"));
      readings.isReadingsValid = false;
      return readings;
    }
    // Compute heat index in Fahrenheit (the default)
    readings.heatIndexFahrenheit = dht.computeHeatIndex(readings.temperatureFahrenheit, readings.humidityPercent);
    // Compute heat index in Celsius (isFahreheit = false)
    readings.heatIndexCelcius = dht.computeHeatIndex(readings.temperatureCelcius, readings.humidityPercent, false);
    readings.isReadingsValid = true;
  
    Serial.print(F("Humidity: "));
    Serial.print(readings.humidityPercent);
    Serial.print(F("%  Temperature: "));
    Serial.print(readings.temperatureCelcius);
    Serial.print(F("°C "));
    Serial.print(readings.temperatureFahrenheit);
    Serial.print(F("°F  Heat index: "));
    Serial.print(readings.heatIndexCelcius);
    Serial.print(F("°C "));
    Serial.print(readings.heatIndexFahrenheit);
    Serial.println(F("°F"));
  }
  
  return readings;
}

void handleLed(String msg){
  setupComponentLed();
  if(msg == "ON"){
    Serial.println("Il est temps d'ouvrir la lumière");
    ledState = HIGH;
  }
  else if (msg == "OFF"){
    Serial.println("Il est temps de fermer la lumière");
    ledState = LOW;
  }
  else{
    Serial.println("Message received doesnt correspond to a led state...");
  }
  digitalWrite(LED_BUILTIN, ledState);
}
