#ifndef DIFFERENTIAL_DRIVE_H
#define DIFFERENTIAL_DRIVE_H

#define DIFFERENTIAL_DRIVE_DEBUG true
#define ROTATIONAL_UPDATE_RATE 50.0 //in Hz

#include <PID_v1.h>
#include "IMU.h"
#include "Misc.h"

#define ROTATIONAL_UPDATE_TIME (1000.0 / ROTATIONAL_UPDATE_RATE)

struct motor
{
    int D0;
    int D1;
    int PWM_PIN;
    constexpr motor(int x, int y, int z) : D0(x), D1(y), PWM_PIN(z)
    {
    }
};

double input, setpoint, output, rot_angle;
float rot_clock = 100.0, rot_anti = -100.0;

PID rotational(&input, &output, &setpoint, 0.0, 0.0, 0.0, DIRECT);

class DifferentialDrive
{
    float L;
    float R;
    float desired_angle;
    motor left_motor;
    motor right_motor;
    int max_velocity;
    void write_motor(float, float);
    void _move(float, float);

public:
    DifferentialDrive(float _L, float _R, motor _left, motor _right, double *_pid_consts, int _max) : L(_L), R(_R), left_motor(_left), right_motor(_right), max_velocity(_max)
    {
        rotational.SetSampleTime(50);
        rotational.SetTunings(_pid_consts[0], _pid_consts[1], _pid_consts[2]);
        rotational.SetOutputLimits(-100.0, 100.0);
        rotational.SetMode(AUTOMATIC);
        desired_angle = 0.0;
        setpoint = 0.0;
    }

    void initialize()
    {
        debug_out("Initializing Drive");
        int pins[] = {left_motor.D0, left_motor.D1, left_motor.PWM_PIN, right_motor.D0, right_motor.D1, right_motor.PWM_PIN};
        for (int pin : pins)
            pinMode(pin, OUTPUT);
    }
    void debug_out(String);
    void move(float, float);
    void stop(bool hard = true);
    void rotate(float, int);
    void setHeading(float);
};

void DifferentialDrive::debug_out(String msg)
{
#if DIFFERENTIAL_DRIVE_DEBUG
    Serial.println("debug : diffDrive :: " + msg);
#endif
}

void DifferentialDrive::write_motor(float _l, float _r)
{

    int l = (int)map_float(_l, -100, 100, -255, 255);
    int r = (int)map_float(_r, -100, 100, -255, 255);
    digitalWrite(left_motor.D0, l > 0);
    digitalWrite(left_motor.D1, l < 0);
    analogWrite(left_motor.PWM_PIN, abs(l));

    digitalWrite(right_motor.D0, r > 0);
    digitalWrite(right_motor.D1, r < 0);
    analogWrite(right_motor.PWM_PIN, abs(r));

    //  debug_out("Left :" + String(l) + "\tRight :" + String(r));
}

void DifferentialDrive::_move(float v, float w)
{
    debug_out("_move:: V:" + String(v) + "\tW:" + String(w));
    float vl = (2 * v - w * L) / (2 * R);
    float vr = (2 * v + w * L) / (2 * R);
    float _max = max(abs(vl), abs(vr));
    float _max_velocity = abs(map_float(v, -100.0, 100.0, -max_velocity, max_velocity));
    vl = _max_velocity * (vl / _max);
    vr = _max_velocity * (vr / _max);
    write_motor(vl, vr);
}

void DifferentialDrive::move(float v, float w = 0)
{
    static uint64_t last_rot_update = millis() - ROTATIONAL_UPDATE_TIME;
    input = angleDiff(getYaw(), desired_angle);
    rotational.Compute();
    debug_out("IN:: " + String(input) + " SET::" + String(setpoint) + " OUT::" + String(output));
    _move(v, w + (float)output);
    if (w != 0.0 && millis() - last_rot_update > ROTATIONAL_UPDATE_TIME)
    {
        last_rot_update = millis();
        desired_angle += w / ROTATIONAL_UPDATE_RATE;
    }
}

void DifferentialDrive::stop(bool hard = true)
{
    int pins[] = {left_motor.D0, left_motor.D1, left_motor.PWM_PIN, right_motor.D0, right_motor.D1, right_motor.PWM_PIN};
    for (int pin : pins)
        digitalWrite(pin, hard);
}

void DifferentialDrive::rotate(float angle_desired, int rot_speed = 15)
{

    float angle = angleDiff(angle_desired, getYaw());
    int dir;

    if (angle >= 0)
        dir = 1;
    else
        dir = 0;

    while (angle > 2.0 && dir == 1)
    {
        write_motor(-rot_speed, rot_speed);
        angle = angleDiff(angle_desired, getYaw());
        //  Serial.println(angle);
    }

    while (angle < -2.0 && dir == 0)
    {
        write_motor(rot_speed, -rot_speed);
        angle = angleDiff(angle_desired, getYaw());
        //  Serial.println(angle);
    }
    this->desired_angle = angle_desired;
    stop();
}

void DifferentialDrive::setHeading(float _desired_angle)
{
    this->desired_angle = _desired_angle;
}

#endif