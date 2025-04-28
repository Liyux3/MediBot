# MediBot

MediBot is an autonomous medical assistance robot built on multiple hardware platforms including Arduino, ESP32, and NVIDIA Jetson Nano. 

In normal mode, it smartly patrols over the buildings, collecting ambient data including temperature, humidity, and air quality data. Additionally, it can perform contactless fever screening and monitor mask compliance. Data will be analyzed and displayed through a user-end web interface in real-time. Meanwhile, an operator can play pre-recorded audio announcements and control the robot's movement manually (when needed) remotely via the web control panel.

Upon detecting smoke or fire, it will transition to emergency mode, play audio alerts to the public and simultaneously send the notifications to operators who can manually dismiss emergency once it is clear.

---

https://github.com/user-attachments/assets/9a6b4d10-532c-44e1-a109-206e84b807f9

----

## Features and Capabilities
### Autonomous Navigation
- Mecanum wheel drive system for omnidirectional movement
- LIDAR-based mapping and obstacle detection 
- PID-controlled precision movement 
### Health and Environmental Monitoring
- Face detection with mask wearing detection
- Temperature and humidity monitoring
- Air quality (gas) detection with alert system
- Thermal imaging for temperature screening
### Remote Control and Monitoring
- Real-time web interface for robot control 
- Live camera feed with mask detection overlay
- Sensor data visualization with charts 
- Remote audio playback for announcements
### Emergency Response
- Automatic alert system for abnormal conditions
- Emergency mode with audio alerts
- Real-time notifications to operators




## Prerequisite:

### Hardware
- NVIDIA Jetson Nano: Main processing unit for computer vision, LIDAR, and system integration
- Arduino Board controls the robot's motors and movement
- ESP32 Module handles WiFi connectivity and sensor data publishing
- Camera for Real-time video feed and mask detection
- Thermal Camera MLX90640: Temperature scanning
- YDLidar for Navigation and mapping
- Motors and Encoders: Movement with 4-wheel mecanum drive system
- BME280 for temperature/humidity
- MQ-135 for air quality monitoring

### Software
#### For Jetson Nano:
- Ubuntu 18.04 with Python 3,6 & Python 2.7 (for ROS)
- OpenCV `cv2`
- Paho MQTT client `paho.mqtt.client`
- ROS Melodic `sudo apt install ros-melodic-desktop`
- Navigation packages `ros-melodic-gmapping, ros-melodic-move-base, ros-melodic-amcl, ros-melodic-map-server, ros-melodic-dwa-local-planner, ros-melodic-tf2-ros`
- YDLidar SDK `https://github.com/YDLIDAR/YDLidar-SDK`
- YDLidar ROS Driver `https://github.com/YDLIDAR/ydlidar_ros_driver`
- NumPy `numpy`
- PyGame `pygame`

#### For Arduino:
- Arduino IDE
- Encoder Library `Encoder`
- PID Library `PID`

#### For ESP32
- Arduino IDE with ESP32 support `Adafruit BME280`
- WiFi Library `WiFi`
- PubSubClient Library `PubSubClient`
- Adafruit Sensor Libraries `Adafruit Sensor`

#### For Web Interface
- Modern web browser
- Chart.js
- MQTT.js




## Navigation & Mapping

To start mapping: `roslaunch mapping.launch`  *Note: `src/real_odom_publisher.py` Reads and processes Arduino odometry.
To start navigation: `roslaunch navigation.launch`

#### How it Works:
1. Arduino reads wheel encoders, calculates speeds `vx`, `vy`, `vth`, sends over Serial
2. `real_odom_publisher.py` converts speeds to position, publishes `TF` and `/odom`
3. `GMapping`/`AMCL` use this with lidar scans for mapping/localization
4. `move_base` plans paths and outputs `/cmd_vel` commands

