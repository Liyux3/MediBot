import json
import time
import threading
import pygame
import os
import paho.mqtt.client as mqtt_client
from camera_handler import CameraHandler
import ydlidar
import cv2
import numpy as np
import math
import pygame
import base64

# MQTT Configuration
broker = 'your-mqtt-broker.example.com'
port = 1883
topics = [
    "Fred_ELEC3848/SayHello",
    "Fred_ELEC3848/Picture",
    "Fred_ELEC3848/Control",
    "Fred_ELEC3848/Web_Switch",
    "Fred_ELEC3848/ELEC3848"
]
client_id = 'Fred-O'
client_pwd = os.environ.get('MQTT_PASSWORD', '')

# Global state variables
current_mode = "Normal"
current_page = None
camera = None
lidar_running = False
emergency_sound_playing = False

# Lidar visualization setup
lidar_width, lidar_height = 800, 800
lidar_center_x, lidar_center_y = lidar_width // 2, lidar_height // 2
lidar_scale = 40  # Pixels per meter
lidar_surface = None
lidar_laser = None

# Initialize pygame for audio
pygame.mixer.init()

# Initialize MQTT client
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Successfully connected to MQTT broker")
            # Subscribe to all topics
            for topic in topics:
                client.subscribe(topic)
                print(f"Subscribed to {topic}")
        else:
            print(f"Failed to connect, return code {rc}")

    client = mqtt_client.Client(client_id)
    client.username_pw_set(client_id, client_pwd)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port)
    return client

# Message handler
def on_message(client, userdata, msg):
    global current_mode, current_page
    
    try:
        payload = msg.payload.decode('utf-8')
        data = json.loads(payload)
        msg_type = data.get("Type")
        
        print(f"Received message type: {msg_type}")
        
        if msg_type == "State_Change":
            state = data.get("State")
            if state in ["Normal", "Emergency"]:
                current_mode = state
                print(f"Mode changed to: {current_mode}")
                
                # Handle emergency mode transition
                if current_mode == "Emergency":
                    start_emergency_mode()
                else:
                    stop_emergency_mode()
                    
        elif msg_type == "Web_Change":
            page = data.get("Page")
            if page:
                current_page = page
                print(f"Active page changed to: {current_page}")
                handle_page_change(page)
                
        elif msg_type == "Play_Music":
            handle_music_command(data)
            
        elif msg_type == "Control":
            # This is handled by web_control.py
            pass
            
    except Exception as e:
        print(f"Error processing message: {e}")

# Page change handler
def handle_page_change(page):
    global camera, lidar_running, lidar_laser
    
    # Release resources from previous page
    if page != "rti_display_html" and camera is not None:
        camera.stop()
        camera = None
        print("Camera resources released")
    
    if page != "lidar_html" and lidar_running:
        stop_lidar()
    
    # Initialize resources for new page
    if page == "rti_display_html" and camera is None:
        camera = CameraHandler()
        camera.start()
        print("Camera initialized")
    
    elif page == "lidar_html" and not lidar_running:
        start_lidar()

# Music playback handler
def handle_music_command(data):
    name = data.get("Name", "")
    enable = data.get("Enable", False)
    
    if enable:
        try:
            path = os.path.join('audio', name)
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(loops=-1)
            print(f"Playing music: {name}")
        except Exception as e:
            print(f"Error playing music: {e}")
    else:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            print("Music stopped")

# Emergency mode handlers
def start_emergency_mode():
    global emergency_sound_playing
    
    if not emergency_sound_playing:
        try:
            # Play emergency sound
            path = os.path.join('audio', 'emergency.mp3')  # Assuming you have this file
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(loops=-1)
            emergency_sound_playing = True
            print("Emergency mode activated - playing warning sound")
            
            # Send emergency notification to web interface
            send_emergency_notification()
        except Exception as e:
            print(f"Error starting emergency mode: {e}")

def stop_emergency_mode():
    global emergency_sound_playing
    
    if emergency_sound_playing:
        pygame.mixer.music.stop()
        emergency_sound_playing = False
        print("Emergency mode deactivated")

# LIDAR functions
def start_lidar():
    global lidar_running, lidar_laser, lidar_surface
    
    try:
        # Initialize pygame surface for LIDAR visualization
        pygame.init()
        lidar_surface = pygame.Surface((lidar_width, lidar_height))
        
        # Initialize YDLIDAR
        print("Initializing YDLIDAR...")
        ydlidar.os_init()
        ports = ydlidar.lidarPortList()
        port = "/dev/ydlidar"  # Default, might need changing
        
        for key, value in ports.items():
            port = value
            print(port)
        
        lidar_laser = ydlidar.CYdLidar()
        
        # Configure YDLIDAR
        lidar_laser.setlidaropt(ydlidar.LidarPropSerialPort, port)
        lidar_laser.setlidaropt(ydlidar.LidarPropSerialBaudrate, 115200)
        lidar_laser.setlidaropt(ydlidar.LidarPropLidarType, ydlidar.TYPE_TRIANGLE)
        lidar_laser.setlidaropt(ydlidar.LidarPropDeviceType, ydlidar.YDLIDAR_TYPE_SERIAL)
        lidar_laser.setlidaropt(ydlidar.LidarPropScanFrequency, 10.0)
        lidar_laser.setlidaropt(ydlidar.LidarPropSampleRate, 7)
        lidar_laser.setlidaropt(ydlidar.LidarPropSingleChannel, True)
        lidar_laser.setlidaropt(ydlidar.LidarPropMaxAngle, 180.0)
        lidar_laser.setlidaropt(ydlidar.LidarPropMinAngle, -180.0)
        lidar_laser.setlidaropt(ydlidar.LidarPropMaxRange, 16.0)
        lidar_laser.setlidaropt(ydlidar.LidarPropMinRange, 0.08)
        lidar_laser.setlidaropt(ydlidar.LidarPropIntenstiy, False)
        
        # Initialize and turn on
        ret = lidar_laser.initialize()
        if not ret:
            print(f"Failed to initialize Lidar on port {port}.")
            print(f"Error: {lidar_laser.DescribeError()}")
            ydlidar.os_shutdown()
            return
        
        ret = lidar_laser.turnOn()
        if not ret:
            print("Failed to turn on Lidar.")
            print(f"Error: {lidar_laser.DescribeError()}")
            lidar_laser.disconnecting()
            ydlidar.os_shutdown()
            return
        
        lidar_running = True
        print("LIDAR started successfully")
        
        # Start LIDAR processing thread
        threading.Thread(target=process_lidar, daemon=True).start()
    
    except Exception as e:
        print(f"Error starting LIDAR: {e}")

def stop_lidar():
    global lidar_running, lidar_laser
    
    if lidar_running and lidar_laser:
        try:
            lidar_running = False
            lidar_laser.turnOff()
            lidar_laser.disconnecting()
            ydlidar.os_shutdown()
            print("LIDAR stopped")
        except Exception as e:
            print(f"Error stopping LIDAR: {e}")

def process_lidar():
    global lidar_running, lidar_laser, lidar_surface
    
    scan = ydlidar.LaserScan()
    
    while lidar_running and ydlidar.os_isOk():
        r = lidar_laser.doProcessSimple(scan)
        
        if r:
            # Clear surface
            lidar_surface.fill((0, 0, 0))  # Black background
            
            # Draw lidar center
            pygame.draw.circle(lidar_surface, (255, 0, 0), (lidar_center_x, lidar_center_y), 5)
            
            # Draw scan points
            for point in scan.points:
                angle = point.angle  # Radians
                range_m = point.range  # Meters
                
                # Filter out invalid points
                if range_m > scan.config.min_range and range_m < scan.config.max_range:
                    # Convert polar to Cartesian
                    x = range_m * math.cos(angle)
                    y = range_m * math.sin(angle)
                    
                    # Convert meters to pixels and adjust for screen coordinates
                    screen_x = lidar_center_x + int(x * lidar_scale)
                    screen_y = lidar_center_y - int(y * lidar_scale)  # Invert Y
                    
                    # Draw the line from center to point (if within bounds)
                    if 0 <= screen_x < lidar_width and 0 <= screen_y < lidar_height:
                        # Use a dimmer color for the lines
                        pygame.draw.line(lidar_surface, (100, 100, 100), 
                                        (lidar_center_x, lidar_center_y), (screen_x, screen_y), 1)
                        # Draw a small white dot at the end point
                        pygame.draw.circle(lidar_surface, (255, 255, 255), (screen_x, screen_y), 2)
            
            # Save and publish the LIDAR visualization
            pygame.image.save(lidar_surface, 'lidar_scan.jpg')
            publish_image('lidar_scan.jpg')
        
        time.sleep(0.1)  # 10 Hz update rate

# Publish image to MQTT
def publish_image(image_path):
    try:
        with open(image_path, 'rb') as file:
            filecontent = file.read()
            encoded = base64.b64encode(filecontent)
            client.publish("Fred_ELEC3848/Picture", encoded, 2)
            print(f"Published image: {image_path}")
    except Exception as e:
        print(f"Error publishing image: {e}")

# Send sensor data to web interface
def send_sensor_data():
    # This would collect data from your sensors and publish it
    # For now, just sending dummy data
    data = {
        "Type": "Sensor_Data",
        "Temperature": 25.5,
        "Humidity": 60.0,
        "Battery": 80,
        "Gas": 400,
        "Mask": True
    }
    
    client.publish("Fred_ELEC3848/SayHello", json.dumps(data))

# Send emergency notification
def send_emergency_notification():
    data = {
        "Type": "Others",
        "Message": "EMERGENCY DETECTED! Robot in emergency mode."
    }
    
    client.publish("Fred_ELEC3848/SayHello", json.dumps(data))

# Main function
def main():
    global client
    
    # Connect to MQTT broker
    client = connect_mqtt()
    client.loop_start()
    
    # Main processing loop
    try:
        while True:
            # Page-specific processing
            if current_page == "index_html":  # Sensor monitor
                # Send sensor data periodically
                send_sensor_data()
                
            elif current_page == "rti_display_html" and camera:  # Camera view
                # Process camera feed
                frame = camera.get_frame()
                if frame is not None:
                    # Save and publish the camera frame
                    cv2.imwrite('camera_frame.jpg', frame)
                    publish_image('camera_frame.jpg')
            
            # Mode-specific processing
            if current_mode == "Emergency":
                # Ensure emergency sound is playing
                if not emergency_sound_playing:
                    start_emergency_mode()
            
            # Sleep to prevent CPU hogging
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("Program terminated by user")
    finally:
        # Cleanup
        if camera:
            camera.stop()
        if lidar_running:
            stop_lidar()
        pygame.quit()
        client.loop_stop()
        client.disconnect()
        print("Program terminated")

if __name__ == "__main__":
    main()