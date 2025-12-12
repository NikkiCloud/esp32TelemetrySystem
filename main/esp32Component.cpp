#include <Arduino.h>

bool ledState = LOW;

void setupComponent(){
  pinMode(LED_BUILTIN, OUTPUT);
}

void handleLed(String msg){
  setupComponent();
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
