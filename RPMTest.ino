/*************************************************************************
* Sample sketch based on OBD-II library for Arduino
*************************************************************************/

#include <Arduino.h>
#include <Wire.h>
#include <OBD.h>

COBD obd;

void setup()
{
  // start communication with OBD-II UART adapter
  obd.begin();
  // initiate OBD-II connection until success
  while (!obd.init()); 
  Serial.println("Connection has been made...");
  char buf[64];
  if (obd.getVIN(buf, sizeof(buf))) {
    Serial.print("VIN: ");
    Serial.println("buf");
  }
}

void loop()
{
  int value;
  if (obd.readPID(PID_RPM, value)) {
    Serial.print("RPM:");
    Serial.println(value);
  }
} 
