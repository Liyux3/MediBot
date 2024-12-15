#include <Arduino.h>
#include <Encoder.h>
#include <PID_v1.h>
// #include "Wheels.h"

long Pos[4];

class Wheel {
    public:
        Wheel(uint8_t pwmPin, uint8_t dirPin1, uint8_t dirPin2, int direction = 1);
        void setPWM(int pwm);
        void setTargetVelocity(float speed);
        void scalePWM(float factor);
        void stop();
        void in();
        void out();
        void moveByVelocity();
        static int base_pwm;
        static int lowest_pwm;
        static int highest_pwm;
        int wheel_pwm;
        double target_velocity;
        double wheel_velosity;
        double wheel_current_velocity;
        int direction;
    private:
        uint8_t pwmPin;
        uint8_t dirPin1;
        uint8_t dirPin2;
};

int Wheel::base_pwm = 90;
int Wheel::lowest_pwm = 30;
int Wheel::highest_pwm = 100;

Wheel::Wheel(uint8_t pwmPin, uint8_t dirPin1, uint8_t dirPin2, int direction = 1) {
    this->pwmPin = pwmPin;
    this->dirPin1 = dirPin1;
    this->dirPin2 = dirPin2;
    this->wheel_pwm = base_pwm;
    this->direction = direction;

    pinMode(this->pwmPin, OUTPUT);
    pinMode(this->dirPin1, OUTPUT);
    pinMode(this->dirPin2, OUTPUT);
};

void Wheel::setPWM(int pwm) {
    this->wheel_pwm = constrain(pwm, lowest_pwm, highest_pwm);
};

void Wheel::setTargetVelocity(float speed) {
    this->target_velocity = double(speed);
};

void Wheel::scalePWM(float factor) {
    this->wheel_pwm = constrain(int(this->wheel_pwm * factor), lowest_pwm, highest_pwm);
    // this->wheel_pwm *= factor;
    // this->stop();
};

void Wheel::stop() {
    digitalWrite(this->dirPin1, LOW);
    digitalWrite(this->dirPin2, LOW);
    analogWrite(this->pwmPin, 0);
};

void Wheel::in() {
    digitalWrite(this->dirPin1, HIGH);
    digitalWrite(this->dirPin2, LOW);
    analogWrite(this->pwmPin, this->wheel_pwm);
};

void Wheel::out() {
    digitalWrite(this->dirPin1, LOW);
    digitalWrite(this->dirPin2, HIGH);
    analogWrite(this->pwmPin, this->wheel_pwm);
};

void Wheel::moveByVelocity() {
    this->wheel_pwm = int(abs(this->target_velocity) * 326);
    if (this->wheel_velosity * direction > 50) {
        this->in();
    } else if (this->wheel_velosity * direction < -50) {
        this->out();
    } else {
        this->stop();
    }
}

// Motor pins
#define PWMFL   12   //Motor Front-Left PWM
#define DIRFL1  34   
#define DIRFL2  35   //Motor FL Direction
#define PWMFR   8    //Motor Front-Right PWM
#define DIRFR1  37   
#define DIRFR2  36   //Motor FR Direction
#define PWMBL   9    //Motor Back-Left PWM --> from 6 to 9
#define DIRBL1  43   
#define DIRBL2  42   //Motor BL Direction
#define PWMBR   5    //Motor Back-Right PWM
#define DIRBR1  A4   //26 - A4
#define DIRBR2  A5   //27 - A5 //Motor BR Direction

// Encoder pins 
#define ENCFL1  18
#define ENCFL2  31
#define ENCFR1  19
#define ENCFR2  38
#define ENCBL1  3
#define ENCBL2  49
#define ENCBR1  2
#define ENCBR2  A1

Wheel wheel_FL(PWMFL, DIRFL1, DIRFL2, -1);
Wheel wheel_FR(PWMFR, DIRFR1, DIRFR2, 1);
Wheel wheel_BL(PWMBL, DIRBL1, DIRBL2, -1);
Wheel wheel_BR(PWMBR, DIRBR1, DIRBR2, 1);
Wheel *wheel_set[4] = {&wheel_FL, &wheel_FR, &wheel_BL, &wheel_BR};

Encoder encoder_FL(ENCFL1, ENCFL2);
Encoder encoder_FR(ENCFR1, ENCFR2);
Encoder encoder_BL(ENCBL1, ENCBL2);
Encoder encoder_BR(ENCBR1, ENCBR2);
Encoder *encoders[4] = {&encoder_FL, &encoder_FR, &encoder_BL, &encoder_BR};

// PID PID_FL(&wheel_FL.wheel_current_velocity, &wheel_FL.wheel_velosity, &wheel_FL.target_velocity, 2.0, 5.0, 1.0, DIRECT);
// PID PID_FR(&wheel_FR.wheel_current_velocity, &wheel_FR.wheel_velosity, &wheel_FR.target_velocity, 2.0, 5.0, 1.0, DIRECT);
// PID PID_BL(&wheel_BL.wheel_current_velocity, &wheel_BL.wheel_velosity, &wheel_BL.target_velocity, 2.0, 5.0, 1.0, DIRECT);
// PID PID_BR(&wheel_BR.wheel_current_velocity, &wheel_BR.wheel_velosity, &wheel_BR.target_velocity, 2.0, 5.0, 1.0, DIRECT);
// // PID *PID_set[4] = {&PID_FL, &PID_FR, &PID_BL, &PID_BR};
float Speed[4] = {0, 0, 0, 0};

// void wheelPIDControl() {
//     PID_FL.Compute();
//     PID_FR.Compute();
//     PID_BL.Compute();
//     PID_BR.Compute();
// }

void setTargetVelocity () {
    wheel_FL.setTargetVelocity(Speed[0]);
    wheel_FR.setTargetVelocity(Speed[1]);
    wheel_BL.setTargetVelocity(Speed[2]);
    wheel_BR.setTargetVelocity(Speed[3]);
}

void setPWM(int new_pwm) {
    Wheel::base_pwm = constrain(new_pwm, Wheel::lowest_pwm, Wheel::highest_pwm);
    wheel_FL.setPWM(Wheel::base_pwm);
    wheel_FR.setPWM(Wheel::base_pwm);
    wheel_BL.setPWM(Wheel::base_pwm);
    wheel_BR.setPWM(Wheel::base_pwm);
}

void adjustSpeedFromAverage(float factor) {
    long avg_dis = wheelAverageDistance();
    // Serial.println(avg_dis);
    // float scale[4] = {(float)tanh((float)(avg_dis - Pos[0]) * factor), (float)tanh((float)(avg_dis - Pos[1]) * factor), (float)tanh((float)(avg_dis - Pos[2]) * factor), (float)tanh((float)(avg_dis - Pos[3]) * factor)};
    // String scales;
    // for (long s : scale) {
    //     scales += s;
    //     scales += ' ';
    // }
    // Serial.println(scales);
    wheel_FL.setPWM(Wheel::base_pwm * (tanh(avg_dis - Pos[0]) * factor + 1.0));
    wheel_FR.setPWM(Wheel::base_pwm * (tanh(avg_dis - Pos[1]) * factor + 1.0));
    wheel_BL.setPWM(Wheel::base_pwm * (tanh(avg_dis - Pos[2]) * factor + 1.0));
    wheel_BR.setPWM(Wheel::base_pwm * (tanh(avg_dis - Pos[3]) * factor + 1.0));
}

//Movement functions:
//  < FL-----FR <
//     |  ↑  |
//     |  |  |
//  < BL-----BR <
void ADVANCE() { wheel_FL.out(); wheel_FR.in(); wheel_BL.out(); wheel_BR.in(); }
//  > FL-----FR <
//     |  ←  |
//     |  ←  |
//  < BL-----BR >
void LEFT_2() { wheel_FL.in(); wheel_FR.in(); wheel_BL.out(); wheel_BR.out(); }
//  > FL-----FR >
//     |  |  |
//     |  ↓  |
//  > BL-----BR >
void BACK() { wheel_FL.in(); wheel_FR.out(); wheel_BL.in(); wheel_BR.out(); }
//  < FL-----FR >
//     |  →  |
//     |  →  |
//  > BL-----BR <
void RIGHT_2() { wheel_FL.out(); wheel_FR.out(); wheel_BL.in(); wheel_BR.in(); }
//  = FL-----FR <
//     |   ↖ |
//     | ↖   |
//  < BL-----BR =
void LEFT_1() { wheel_FL.stop(); wheel_FR.in(); wheel_BL.out(); wheel_BR.stop(); }
//  < FL-----FR =
//     | ↗   |
//     |   ↗ |
//  = BL-----BR <
void RIGHT_1() { wheel_FL.out(); wheel_FR.stop(); wheel_BL.stop(); wheel_BR.in(); }
//  > FL-----FR =
//     | ↙   |
//     |   ↙ |
//  = BL-----BR >
void LEFT_3() { wheel_FL.in(); wheel_FR.stop(); wheel_BL.stop(); wheel_BR.out(); }
//  = FL-----FR >
//     |   ↘ |
//     | ↘   |
//  > BL-----BR =
void RIGHT_3() { wheel_FL.stop(); wheel_FR.out(); wheel_BL.in(); wheel_BR.stop(); }
//  < FL-----FR >
//     | ↗ ↘ |
//     | ↖ ↙ |
//  < BL-----BR >
void rotate_1() { wheel_FL.out(); wheel_FR.out(); wheel_BL.out(); wheel_BR.out(); }
//  > FL-----FR <
//     | ↙ ↖ |
//     | ↘ ↗ |
//  > BL-----BR <
void rotate_2() { wheel_FL.in(); wheel_FR.in(); wheel_BL.in(); wheel_BR.in(); }
//  = FL-----FR =
//     |  =  |
//     |  =  |
//  = BL-----BR =
void STOP() { wheel_FL.stop(); wheel_FR.stop(); wheel_BL.stop(); wheel_BR.stop(); }

void collectWheelPos() {
    noInterrupts();
    Pos[0] = encoder_FL.read();
    Pos[1] = encoder_FR.read();
    Pos[2] = encoder_BL.read();
    Pos[3] = encoder_BR.read();
    interrupts();
}

void resetWheelPos() {
    encoder_FL.write(0);
    encoder_FR.write(0);
    encoder_BL.write(0);
    encoder_BR.write(0);
    for (int i = 0; i < 4; i++) Pos[i] = 0;
}

void printWheelPos() {
    String positions;
    for (long p : Pos) {
        positions += p;
        positions += ' ';
    }
    Serial.println(positions);
}

long wheelAverageDistance() {
    long sum = 0;
    int count = 0;
    for (long p : Pos) {
        sum += abs(p);
        if (p != 0) count += 1;
    }
    return sum / count;
}


// Odometry constants
const float TICKS_PER_REVOLUTION = 1320.0;
const float WHEEL_DIAMETER = 0.08;
const float WHEEL_RADIUS = WHEEL_DIAMETER / 2.0;
// Distance from center of robot to wheel contact point, parallel to robot's X axis (forward)
const float WHEEL_LX = 0.1025; // meters (Half your WHEEL_BASE: 20.5 / 2)
// Distance from center of robot to wheel contact point, parallel to robot's Y axis (sideways)
const float WHEEL_LY = 0.0825; // meters (Half the track width: 16.5 / 2)

// Calculated constant
const float DISTANCE_PER_TICK = (PI * WHEEL_DIAMETER) / TICKS_PER_REVOLUTION; // Meters per tick

// Odometry calculation interval
const unsigned long ODOM_INTERVAL_MS = 50; // Calculate and send odometry every 50ms (20 Hz)

// --- Global Variables for Odometry ---
unsigned long last_odom_time = 0;
// Need previous ticks for each wheel for Mecanum calculation
long prev_raw_ticks_FL = 0;
long prev_raw_ticks_FR = 0;
long prev_raw_ticks_BL = 0;
long prev_raw_ticks_BR = 0;

char action;
bool move_done = true;
double target_wheel_turns;
float target_velocity_x = 0.0;
float target_velocity_y = 0.0;
float target_velocity_th = 0.0;

void odom() {
    // --- Odometry Calculation and Publishing ---
    unsigned long current_time = millis();
    if (current_time - last_odom_time >= ODOM_INTERVAL_MS) {
        float interval_seconds = (float)(current_time - last_odom_time) / 1000.0;
        if (interval_seconds <= 0) interval_seconds = 0.0001; // Avoid division by zero if loop is too fast
        last_odom_time = current_time;

        // Get current raw ticks for ALL wheels
        long current_raw_ticks_FL = encoder_FL.read();
        long current_raw_ticks_FR = encoder_FR.read();
        long current_raw_ticks_BL = encoder_BL.read();
        long current_raw_ticks_BR = encoder_BR.read();

        // Calculate change in ticks since last interval
        long delta_ticks_FL = current_raw_ticks_FL - prev_raw_ticks_FL;
        long delta_ticks_FR = current_raw_ticks_FR - prev_raw_ticks_FR;
        long delta_ticks_BL = current_raw_ticks_BL - prev_raw_ticks_BL;
        long delta_ticks_BR = current_raw_ticks_BR - prev_raw_ticks_BR;

        // Update previous ticks for next loop
        prev_raw_ticks_FL = current_raw_ticks_FL;
        prev_raw_ticks_FR = current_raw_ticks_FR;
        prev_raw_ticks_BL = current_raw_ticks_BL;
        prev_raw_ticks_BR = current_raw_ticks_BR;

        // Calculate individual wheel angular speeds (rad/s)
        float wheel_speed_FL = (float)delta_ticks_FL * (2.0 * PI / TICKS_PER_REVOLUTION) / interval_seconds;
        float wheel_speed_FR = (float)delta_ticks_FR * (2.0 * PI / TICKS_PER_REVOLUTION) / interval_seconds;
        float wheel_speed_BL = (float)delta_ticks_BL * (2.0 * PI / TICKS_PER_REVOLUTION) / interval_seconds;
        float wheel_speed_BR = (float)delta_ticks_BR * (2.0 * PI / TICKS_PER_REVOLUTION) / interval_seconds;

        Speed[0] = wheel_speed_FL;
        Speed[1] = wheel_speed_FR;
        Speed[2] = wheel_speed_BL;
        Speed[3] = wheel_speed_BR;

        // Mecanum Inverse Kinematics (Calculate robot vx, vy, vth from wheel speeds)
        // Assumes standard Mecanum setup (+45 deg rollers FL/BR, -45 deg FR/BL relative to fwd)
        // VERIFY YOUR WHEEL ORIENTATION AND ADJUST SIGNS IF NEEDED!
        float vx  = ( -wheel_speed_FL + wheel_speed_FR - wheel_speed_BL + wheel_speed_BR) * (WHEEL_RADIUS / 4.0);
        float vy  = ( wheel_speed_FL + wheel_speed_FR - wheel_speed_BL - wheel_speed_BR) * (WHEEL_RADIUS / 4.0); // Positive vy = strafe left
        float vth = ( wheel_speed_FL + wheel_speed_FR + wheel_speed_BL + wheel_speed_BR) * (WHEEL_RADIUS / (4.0 * (WHEEL_LX + WHEEL_LY))); // Positive vth = rotate CCW
        // Send over Serial (Format: "ODOM,<vx>,<vy>,<vth>\n")
        Serial.print("ODOM,");
        Serial.print(vx, 4);
        Serial.print(",");
        Serial.print(vy, 4); // Sending vy now!
        Serial.print(",");
        Serial.print(vth, 4);
        Serial.println();
    }
}

void readCommand() {
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');
        int colonIndex = command.indexOf(':'); // Find the position of the colon
        if (colonIndex != -1) {
            action = command.substring(0, colonIndex).charAt(0); // Extract the character before the colon
            target_wheel_turns = (command.substring(colonIndex + 1).toFloat()) / DISTANCE_PER_TICK; // Extract the number after the colon

            if (target_wheel_turns > 0) {
                move_done = false;
                resetWheelPos();
                setPWM(90);
                // Serial.println("Command received, start moving...");
            }
            // else Serial.println("Invalid distance: Must be positive.");
        }
        else {
            // Serial.println("Invalid command. Use <char>:<int>.");
        }
    }
}

void moveByCommand() {
    // IGNORE this one
    // Movement directions ("·" means the car):
    // Q W E    J: head turns left (counter-clockwise)
    // A · D    K: head turns right (clockwise)
    // Z X C    S: stop

    // this is the new one
    // WASD as 4 directions, Q for CCW and E for CW

    switch (action)
    {
        case 'W': {
            ADVANCE();
            break;
        };
        // case 'E': {
        //     RIGHT_1();
        //     break;
        // };
        case 'D': {
            RIGHT_2();
            break;
        // };
        // case 'C': {
        //     RIGHT_3();
        //     break;
        // };
        // case 'X': {
        //     STOP();
        //     move_done = true;
        //     break;
        // };
        // case 'Z': {
        //     LEFT_3();
        //     break;
        // };
        case 'A': {
            LEFT_2();
            break;
        };
        // case 'Q': {
        //     LEFT_1();
        //     break;
        // };
        case 'E': {
            rotate_1();
            break;
        };
        case 'Q': {
            rotate_2();
            break;
        };
        case 'S': {
            BACK();
            break;
        };
        case 'P': {
            for (long p : Pos) Serial.println(p);
            move_done = true;
            break;
        };
        default:
            // Serial.println("Invalid action, aborted.");
            move_done = true;
            break;
    }
}}



float Kp = 1.5;   // Proportional gain
float Ki = 0.05;  // Integral gain
float Kd = 0.3;   // Derivative gain

long previousError = 0;
float integral = 0;

void pidControl() {
    long currentPosition = wheelAverageDistance(); // Or average of all wheels
    long error = target_wheel_turns - currentPosition;

    // Proportional term
    float proportional = Kp * error;

    // Integral term
    integral += error;
    integral = constrain(integral, -100, 100); // Limit integral windup
    float integralTerm = Ki * integral;

    // Derivative term
    float derivative = Kd * (error - previousError);
    previousError = error;
    float derivativeTerm = derivative;

    // Calculate output
    float output = proportional + integralTerm + derivativeTerm;

    // Motor control based on output
    // Adjust motor speeds based on the 'output' value
    // For example:
    setPWM(output / 8);
}

void setup() {
    Serial.begin(115200);
    setPWM(100);
    // attachEncoderInterrupts();
    resetWheelPos();

    // move_done = false;
    // action = 'W';
    // target_wheel_turns = 10 * 1320;
}

void loop() {
    readCommand();
    if (!move_done) {
        pidControl();
        collectWheelPos();
        odom();

        adjustSpeedFromAverage(0.09);
        moveByCommand();
        if (wheelAverageDistance() >= target_wheel_turns) {
            STOP();
            move_done = true;
            Serial.println("Move finished.");
        };
    }
}