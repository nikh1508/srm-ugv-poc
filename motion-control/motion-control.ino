#include "lib/differential_drive.h"
constexpr float L = 0.285;
constexpr float R = 0.05;
constexpr int motor_l_ppm = 7;
constexpr int motor_r_ppm = 8;

#include<PID_Tuner.h>

constexpr motor left = {9, 8, 7};
constexpr motor right = {10, 13, 12};

double pid_const[] = {18.481, 1.072, 3.041};

DifferentialDrive bot(L, R, left, right, pid_const, 50);

float kp, ki, kd;
bool power;

PIDTuner tuner(&power, &kp, &ki, &kd, Serial2);

int v = 0, w = 0;
float angle;
////////////////////////////////////////serial event
#define PORT Serial2
void TIM3_Setup();
byte velocity_recv;
float angle_desired_recv, angle_current_recv;
bool serial_event_enabled = false;
////////////////////////////////////////
void manuver(byte v, float current, float desired);

void setup()
{
  Serial.begin(115200);
  initializeBNO();
  bot.initialize();
  //////serial event
  TIM3_Setup();
  PORT.begin(9600);
  serial_event_enabled = true;

}


bool prevStopped = true, fwd = false;
//

void loop()
{
  manuver(velocity_recv, angle_current_recv, angle_desired_recv);

  //PID_move();  
}
//////////////////////////Serial event
ISR(TIMER3_COMPA_vect)  // called every 48ms
{
  if (serial_event_enabled) {
    serialEvent();
  }
}
