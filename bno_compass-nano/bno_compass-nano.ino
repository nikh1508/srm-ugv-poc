#include "IMU.h"
void setup()
{
  Wire.begin();
  Serial.begin(115200);
  writeCalib();
  initializeBNO();
}

void loop() {
  if (Serial.available()) {
    char ch = Serial.read();
    if (ch == 'g') {
      Serial.println(getYaw());
    }
    else if (ch == 'c') {
      uint64_t last_print = millis() - 100;
      while (!storeCalib()) {
        if (millis() - last_print > 100) {
          last_print = millis();
          Serial.println(calibString());
        }
      }
      delay(200);
      Serial.println(calibString());
      Serial.println("Calibrated and Offsets stored in EEPROM.");
    }
  }
}
