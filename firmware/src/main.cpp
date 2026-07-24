#include <Arduino.h>

void setup() {
  Serial.begin(115200);
  Serial.println("travelweave_device_ready");
}

void loop() {
  delay(1000);
}
