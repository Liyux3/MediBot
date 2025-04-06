/* 
* File name: Arduino_Ros_Control.cpp
* With enough luck, I will be able to receive control command from the JetsonNano via ros serial, and solve the problem
*
* Basic function: Receive String commands and actions TESTED
* Advanced function: Receive velocity command + Send car encoder msg
* Publish encoder data to topic : left_front_encoder, left_rear_encoder, right_front_encoder, right_rear_encoder
*/

#include <Arduino.h>
#include <ros.h>
#include <std_msgs/String.h>
#include <std_msgs/Int32.h>
#include "Wheels.h" 

// Custom headers

bool Motion_Done = true;
const int MOTION_TIME = 50; // In ms

int motorVelFL = 0;
int motorVelBL = 0;
int motorVelFR = 0;
int motorVelBR = 0;

// New publisher variables for republishing web_command messages
std_msgs::String webCommandMsg;
ros::Publisher webCommandPublisher("web_command_executed", &webCommandMsg);

// Basic callback: processes strings from "web_command" topic and then republishes them
void callback(const std_msgs::String &command_msg)
{
  String s = command_msg.data;

  String delimiter = " ";
  int spaceIndex = s.indexOf(delimiter);
  String dir = s.substring(0, spaceIndex);
  String value = s.substring(spaceIndex + 1);

  // Process commands
  if (dir == "W") { Motion_Done = false; ADVANCE(); delay(MOTION_TIME); }
  else if (dir == "A") { Motion_Done = false; LEFT_2(); delay(MOTION_TIME); }
  else if (dir == "S") { Motion_Done = false; BACK(); delay(MOTION_TIME); }
  else if (dir == "D") { Motion_Done = false; RIGHT_2(); delay(MOTION_TIME); }
  else if (dir == "Q") { Motion_Done = false; rotate_2(); delay(MOTION_TIME); }
  else if (dir == "E") { Motion_Done = false; rotate_1(); delay(MOTION_TIME); }
  else if (dir == "X") { Motion_Done = false; STOP(); delay(MOTION_TIME); }

  // Publish the received command to the new topic "web_command_executed"
  webCommandMsg.data = command_msg.data;
  webCommandPublisher.publish(&webCommandMsg);
}

void callBackFunctionMotorFLeft(const std_msgs::Int32 &motorVelocityROS){
  motorVelFL = motorVelocityROS.data;
}
void callBackFunctionMotorBLeft(const std_msgs::Int32 &motorVelocityROS){
  motorVelBL = motorVelocityROS.data;
}
void callBackFunctionMotorFRight(const std_msgs::Int32 &motorVelocityROS){
  motorVelFR = motorVelocityROS.data;
}
void callBackFunctionMotorBRight(const std_msgs::Int32 &motorVelocityROS){
  motorVelBR = motorVelocityROS.data;
}

ros::NodeHandle nh;
ros::Subscriber<std_msgs::String> sub("web_command", &callback); // Basic function

// Advanced functions
// For encoder values publish
std_msgs::Int32 FL_Encoder_ROS;
std_msgs::Int32 BL_Encoder_ROS;
std_msgs::Int32 FR_Encoder_ROS;
std_msgs::Int32 BR_Encoder_ROS;

ros::Publisher front_leftEncoderROSPublisher("left_front_encoder", &FL_Encoder_ROS);
ros::Publisher back_leftEncoderROSPublisher("left_rear_encoder", &BL_Encoder_ROS);
ros::Publisher front_rightEncoderROSPublisher("right_front_encoder", &FR_Encoder_ROS);
ros::Publisher back_rightEncoderROSPublisher("right_rear_encoder", &BR_Encoder_ROS);

// For receiving velocity cmd
ros::Subscriber<std_msgs::Int32> front_leftMotorROSSubscriber("front_left_motor_velocity", &callBackFunctionMotorFLeft);  
ros::Subscriber<std_msgs::Int32> back_leftMotorROSSubscriber("back_left_motor_velocity", &callBackFunctionMotorBLeft);  
ros::Subscriber<std_msgs::Int32> front_rightMotorROSSubscriber("front_right_motor_velocity", &callBackFunctionMotorFRight);  
ros::Subscriber<std_msgs::Int32> back_rightMotorROSSubscriber("back_right_motor_velocity", &callBackFunctionMotorBRight);  

void setup()
{
  nh.initNode();

  nh.subscribe(sub);
  
  // Advertise the new publisher for web_command_executed
  nh.advertise(webCommandPublisher);

  // Uncomment these if you need to subscribe to motor commands or advertise encoder publishers
  // nh.subscribe(front_leftMotorROSSubscriber);
  // nh.subscribe(back_leftMotorROSSubscriber);
  // nh.subscribe(front_rightMotorROSSubscriber);
  // nh.subscribe(back_rightMotorROSSubscriber);
  
  // Also, if encoder publishing is needed, advertise them uncommenting the following:
  // nh.advertise(front_leftEncoderROSPublisher);
  // nh.advertise(back_leftEncoderROSPublisher);
  // nh.advertise(front_rightEncoderROSPublisher);
  // nh.advertise(back_rightEncoderROSPublisher);
  nh.loginfo("Arduino node is online");
}

void loop()
{
  nh.spinOnce();
  // Encoder reading and publishing code (if used) goes here, for example:
  // FL_Encoder_ROS.data = Wheel_FL.readEncoder();
  // front_leftEncoderROSPublisher.publish(&FL_Encoder_ROS);

  delay(1000);
}