#ifndef IMU_H
#define IMU_H
#include "Misc.h"
constexpr int BNO_ADDR = 0x29;
constexpr int BNO_ID = 0xA0;
constexpr int BNO_ID_READ = 0x00;
constexpr int BNO_OPR_MODE = 0x3D;
constexpr int BNO_CONFIG = 0x00;
constexpr int BNO_NDOF = 0x0C;
constexpr int BNO_COMPASS = 0x09;
constexpr int BNO_EUL_HEADING_LSB = 0x1A;
constexpr int BNO_SYS_TRIGGER = 0x3F;
constexpr int SAMPLE_TIME = 10; //Minimum Time interval between each Reading
constexpr int CALIB_STAT = 0x35;
constexpr int NDOF_FMC_OFF = 0x0B;
constexpr int CONFIGMODE = 0x0B;

#define CALIB_STATUS getCalib()

static double yawOffset = 0.0;
static byte data[2];
static bool crystal = false;
static float yaw = 0.0;
constexpr int W_SAMPLE_RATE = 50;
bool newW = false;
double calculatedW = 0.0;


float getYaw();

void setModeBNO(byte mode)
{
  writeByte(BNO_ADDR, BNO_OPR_MODE, mode);
  delay(30);
}

void setCrystalUseBNO(bool cond)
{
  crystal = cond;
  setModeBNO(BNO_CONFIG);
  if (cond)
    writeByte(BNO_ADDR, BNO_SYS_TRIGGER, 0x80);
  else
    writeByte(BNO_ADDR, BNO_SYS_TRIGGER, 0);
  delay(10);
  setModeBNO(BNO_NDOF);
}

void initializeBNO()
{
  debug_msg("Initializing BNO055");
  setModeBNO(BNO_NDOF);//changed mode
  //    for (int i = 0; i < 50; i++)
  //    {
  //        readBytes(BNO_ADDR, BNO_EUL_HEADING_LSB, 2, data);
  //        yawOffset += ((uint16_t)data[1] << 8) | data[0];
  //    }
  //    yawOffset /= 800.0;
  debug_msg("BNO Initialization Complete.");
  debug_msg("Yaw Offset = " + String(yawOffset));
}

void calcW()
{
  static double lastYaw = 0.0;
  double nowYaw = getYaw();
  calculatedW = map2(angleDiff(nowYaw, lastYaw), -12.0, 12.0, -1.0, 1.0);
  lastYaw = nowYaw;
}

float getYaw()
{
  static long lastRead = millis() - SAMPLE_TIME;
  static long lastWCalc = millis() - W_SAMPLE_RATE;
  long currentTime = millis();
  if ((currentTime - lastRead) < SAMPLE_TIME)
    return yaw;
  lastRead = currentTime;
  readBytes(BNO_ADDR, BNO_EUL_HEADING_LSB, 2, data);
  yaw = ((uint16_t)data[1] << 8) | data[0];
  yaw /= 16.0;
  yaw -= yawOffset;
  if (yaw < 0)
  {
    yaw += 360.0;
  }
  currentTime = millis();
  if ((currentTime - lastWCalc) > W_SAMPLE_RATE)
  {
    newW = true;
    calcW();
    lastWCalc = currentTime;
  }
  return yaw;
}

void resetBNO()
{
  debug_msg("Resetting BNO055");
  setModeBNO(BNO_CONFIG);
  writeByte(BNO_ADDR, BNO_SYS_TRIGGER, 0x20);
  while (readByte(BNO_ADDR, BNO_ID_READ) != BNO_ID)
  {
    delay(10);
  }
  delay(50);
  writeByte(BNO_ADDR, BNO_SYS_TRIGGER, 0x0);
  delay(10);
  initializeBNO();
}
uint8_t getCalib() {
  return readByte(BNO_ADDR, CALIB_STAT);
}

String calibString() {
  byte calib_status = CALIB_STATUS;
  byte _system = calib_status >> 6 & 0x3;
  byte gyro = calib_status >> 4 & 0x3;
  byte acc = calib_status >> 2 & 0x3;
  byte mag = calib_status & 0x3;
  return ("CALIB_STAT:: System: " + String(_system) + "\tGYRO: " + String(gyro) + "\tACC: " + String(acc) + "\tMAG: " + String(mag));
}

bool storeCalib() {
  if (CALIB_STATUS == 255) {
    byte calib_byte = 0x55;
    for (int i = 0; i < 22; i++) {
      EEPROM.write(readByte(BNO_ADDR, calib_byte), i);
      calib_byte++;
      delay(10);
    }
    return true;
  }
  return false;
}

void writeCalib() {
  setModeBNO(CONFIGMODE);
  delay(50);
  byte calib_byte = 0x55;
  for (int i = 0; i < 22; i++) {
    writeByte(BNO_ADDR, calib_byte, EEPROM.read(i));
    calib_byte++;
    delay(10);
  }
}
#endif
