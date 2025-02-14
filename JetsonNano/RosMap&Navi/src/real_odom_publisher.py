#!/usr/bin/env python



import rospy
import serial
import math
import tf2_ros # Use tf2 for modern TF handling
from geometry_msgs.msg import TransformStamped, Quaternion, Twist
from nav_msgs.msg import Odometry
# If tf_conversions is not easily available or causes issues, we can do manual quaternion conversion
# import tf_conversions

# --- Configuration ---
SERIAL_PORT = '/dev/ttyUSB0' # Or whatever port your Arduino is on
BAUD_RATE = 115200
ODOM_FRAME = 'odom'
BASE_FRAME = 'base_link'
PUB_RATE = 20 # Rate to publish odom messages (Hz), should match Arduino ideally

# --- Global Variables ---
ser = None
x_pos = 0.0
y_pos = 0.0
theta = 0.0
last_time = None

def main():
    global ser, x_pos, y_pos, theta, last_time

    rospy.init_node('real_odom_publisher')
    rospy.loginfo("Starting Real Odometry Publisher Node")

    # --- Serial Port Setup ---
    serial_port_param = rospy.get_param('~serial_port', SERIAL_PORT)
    baud_rate_param = rospy.get_param('~baud_rate', BAUD_RATE)

    try:
        ser = serial.Serial(serial_port_param, baud_rate_param, timeout=0.1)
        rospy.loginfo("Connected to Arduino on %s at %d baud.", serial_port_param, baud_rate_param)
    except serial.SerialException as e:
        rospy.logerr("Error opening serial port %s: %s", serial_port_param, e)
        return # Exit if serial fails

    # --- ROS Publishers ---
    odom_pub = rospy.Publisher('/odom', Odometry, queue_size=10)
    tf_broadcaster = tf2_ros.TransformBroadcaster()

    rate = rospy.Rate(PUB_RATE)
    last_time = rospy.Time.now()

    # --- Main Loop ---
    while not rospy.is_shutdown():
        current_time = rospy.Time.now()
        dt = (current_time - last_time).to_sec()
        last_time = current_time

        vx_from_arduino = 0.0
        vy_from_arduino = 0.0
        vth_from_arduino = 0.0

        # --- Read from Serial ---
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                # rospy.loginfo_throttle(1.0, "Serial received: %s", line) # Debugging
                if line.startswith("ODOM,"):
                    parts = line.split(',')
                    if len(parts) == 4: # Expect ODOM, vx, vy, vth
                        try:
                            vx_from_arduino = float(parts[1])
                            vy_from_arduino = float(parts[2])
                            vth_from_arduino = float(parts[3])
                            # rospy.loginfo_throttle(0.5,"Parsed Odom: vx=%.3f, vy=%.3f, vth=%.3f", vx_from_arduino, vy_from_arduino, vth_from_arduino) # Debugging
                        except ValueError:
                            rospy.logwarn_throttle(5.0, "Could not parse odom values from: %s", line)
                    else:
                         rospy.logwarn_throttle(5.0, "Incorrect number of parts in ODOM message: %s", line)

        except serial.SerialException as e:
            rospy.logerr("Serial read error: %s. Attempting to reconnect...", e)
            try:
                ser.close()
                ser.open()
                rospy.loginfo("Reconnected to serial port.")
            except serial.SerialException as e2:
                rospy.logerr("Failed to reconnect: %s", e2)
                rospy.sleep(1.0) # Wait before trying again
            continue # Skip rest of loop iteration on error
        except OSError as e:
             rospy.logerr("Serial read OS error: %s.", e) # Can happen if device disconnects
             rospy.sleep(1.0)
             continue


        # --- Integrate Odometry (Calculate Pose Change) ---
        # Calculate change in the robot's frame
        delta_x_robot = vx_from_arduino * dt
        delta_y_robot = vy_from_arduino * dt # Sideways motion
        delta_th = vth_from_arduino * dt

        # Transform change to the odom frame
        delta_x = delta_x_robot * math.cos(theta) - delta_y_robot * math.sin(theta)
        delta_y = delta_x_robot * math.sin(theta) + delta_y_robot * math.cos(theta)

        # Update pose
        x_pos += delta_x
        y_pos += delta_y
        theta += delta_th

        # --- Publish TF Transform (odom -> base_link) ---
        t = TransformStamped()
        t.header.stamp = current_time
        t.header.frame_id = ODOM_FRAME
        t.child_frame_id = BASE_FRAME

        t.transform.translation.x = x_pos
        t.transform.translation.y = y_pos
        t.transform.translation.z = 0.0

        # Need to convert yaw (theta) to quaternion
        # Using manual calculation to avoid tf_conversions dependency if needed
        cy = math.cos(theta * 0.5)
        sy = math.sin(theta * 0.5)
        cp = 1.0 # cos(pitch * 0.5) -> pitch = 0
        sp = 0.0 # sin(pitch * 0.5)
        cr = 1.0 # cos(roll * 0.5) -> roll = 0
        sr = 0.0 # sin(roll * 0.5)

        q = Quaternion()
        q.w = cr * cp * cy + sr * sp * sy
        q.x = sr * cp * cy - cr * sp * sy
        q.y = cr * sp * cy + sr * cp * sy
        q.z = cr * cp * sy - sr * sp * cy
        t.transform.rotation = q

        tf_broadcaster.sendTransform(t)

        # --- Publish Odometry Message (/odom topic) ---
        odom = Odometry()
        odom.header.stamp = current_time
        odom.header.frame_id = ODOM_FRAME
        odom.child_frame_id = BASE_FRAME

        # Set the pose
        odom.pose.pose.position.x = x_pos
        odom.pose.pose.position.y = y_pos
        odom.pose.pose.position.z = 0.0
        odom.pose.pose.orientation = q # Use the same quaternion

        # Set the velocity
        odom.twist.twist.linear.x = vx_from_arduino
        odom.twist.twist.linear.y = vy_from_arduino # Include vy
        odom.twist.twist.angular.z = vth_from_arduino

        # Set covariance (optional, setting to unknown for now)
        # odom.pose.covariance = [...]
        # odom.twist.covariance = [...]

        odom_pub.publish(odom)

        rate.sleep()

    # --- Shutdown ---
    if ser and ser.is_open:
        ser.close()
        rospy.loginfo("Serial port closed.")

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
    finally:
         # Ensure serial port is closed on exit
        if ser and ser.is_open:
            ser.close()
            rospy.loginfo("Serial port closed.")