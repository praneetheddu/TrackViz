/*************************************************************************
* Sample sketch based on OBD-II library for Arduino
*************************************************************************/

#include <Arduino.h>
#include <Wire.h>
#include <OBD.h>
#include <MPU9150.h>
#include <I2Cdev.h>

/**************************************
* Accelerometer & Gyro
**************************************/
#define USE_MPU9150 1
#define ACC_DATA_RATIO 160
#define GYRO_DATA_RATIO 256
#define COMPASS_DATA_RATIO 8

/**************************************
* Timeout/interval options
**************************************/
#define ACC_DATA_INTERVAL 200 /* ms */
int RIPPUM;
int TEMP;
int SPEED;
int acc[3];
int gyro[3];
int temp;
COBD obd;

void processMEMS()
{
    if (!obd.memsRead(acc, gyro, 0, &temp)) return;
    
    acc[0] /= ACC_DATA_RATIO;
    acc[1] /= ACC_DATA_RATIO;
    acc[2] /= ACC_DATA_RATIO;
    gyro[0] /= GYRO_DATA_RATIO;
    gyro[1] /= GYRO_DATA_RATIO;
    gyro[2] /= GYRO_DATA_RATIO;
}



void setup()
{
  Wire.begin();
  Serial.begin(115200);
  Serial.println("Initializing I2C devices...");
  // start communication with OBD-II UART adapter
  obd.begin();
  // initiate OBD-II connection until success
  while (!obd.init(PROTO_AUTO)); 
  Serial.println("Connection has been made...");
  char buf[64];
  if (obd.getVIN(buf, sizeof(buf))) {
      Serial.print("VIN:");
      Serial.println(buf);
  }
  obd.memsInit();
}

void loop()
{
  obd.readPID(PID_RPM, RIPPUM);
  obd.readPID(PID_COOLANT_TEMP, TEMP);
  obd.readPID(PID_SPEED, SPEED);
  processMEMS();
  Serial.print(RIPPUM);
  Serial.print(" ");
  Serial.print(TEMP);
  Serial.print(" ");
  Serial.print(SPEED);
  Serial.print(" ");
  Serial.print(acc[0]);
  Serial.print(" ");
  Serial.print(acc[1]);
  Serial.print(" ");
  Serial.print(acc[2]); 
  Serial.print(" ");
  Serial.print(gyro[0]);
  Serial.print(" ");
  Serial.print(gyro[1]);
  Serial.print(" ");
  Serial.println(gyro[2]); 
} 
