#include <Arduino.h>
#include <WiFi.h>
#include "secrets.h"

void connectToWifi(){
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PWD);

  Serial.println("Connecting to wifi... pls wait...");
  while(WiFi.status() != WL_CONNECTED){
    Serial.print('.');
    delay(250);
  }
  Serial.println(String("Connected to the Wifi network : ") + WIFI_SSID);
  Serial.println(String("Local ESP32 IP : ") + WiFi.localIP());
}

void reconnectToWifi(){
  if(WiFi.status()!= WL_CONNECTED){
    WiFi.reconnect();
  }
}
