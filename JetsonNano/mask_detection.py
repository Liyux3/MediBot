# mask_detection.py - Updated for older OpenCV
import cv2
import numpy as np
import os
import json
import paho.mqtt.client as mqtt

# MQTT broker settings
broker = "broker.emqx.io"
port = 1883
topic = "Fred_ELEC3848/SayHello"
client_id = "JetsonNano"

class MaskDetector:
    def __init__(self):
        # Find the haar cascade file
        cascade_path = '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml'
        # If that doesn't exist, try these alternatives
        if not os.path.exists(cascade_path):
            cascade_path = '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml'
        if not os.path.exists(cascade_path):
            cascade_path = '/usr/local/share/opencv4/haarcascades/haarcascade_frontalface_default.xml'
        if not os.path.exists(cascade_path):
            cascade_path = '/usr/local/share/opencv/haarcascades/haarcascade_frontalface_default.xml'

        # Load face detector
        self.face_detector = cv2.CascadeClassifier(cascade_path)

        # Initialize and configure MQTT client
        self.client = mqtt.Client(client_id)
        self.client.on_connect = self.on_connect

        try:
            self.client.connect(broker, port, keepalive=60)
        except Exception as e:
            print(f"MQTT connection failed: {e}")
        # Start loop in a separate thread
        self.client.loop_start()

        if self.face_detector.empty():
            raise ValueError(f"Error: Could not load face cascade from {cascade_path}")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            client.connected_flag = True
            print("Connected to MQTT broker")
        else:
            print(f"Failed to connect, return code {rc}")

    def publish_mask_status(self, mask_status):
        # Publish JSON data with the format:
        # {"Type": "Sensor_Data", "Mask": true} or {"Type": "Sensor_Data", "Mask": false}
        data = {
            "Type": "Sensor_Data",
            "Mask": True if mask_status == "Mask" else False
        }
        self.client.publish(topic, json.dumps(data))
        print(f"Published: {data}")

    def detect(self, frame):
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = self.face_detector.detectMultiScale(gray, 1.1, 4)
        results = []
        for (x, y, w, h) in faces:
            # Check lower half of face for potential mask colors
            lower_face = frame[y + h // 2:y + h, x:x + w]
            hsv = cv2.cvtColor(lower_face, cv2.COLOR_BGR2HSV)

            # Define ranges for blue, green, and white colors
            lower_blue = np.array([90, 50, 50])
            upper_blue = np.array([130, 255, 255])
            lower_green = np.array([40, 50, 50])
            upper_green = np.array([80, 255, 255])
            lower_white = np.array([0, 0, 200])
            upper_white = np.array([180, 30, 255])

            # Create masks
            mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
            mask_green = cv2.inRange(hsv, lower_green, upper_green)
            mask_white = cv2.inRange(hsv, lower_white, upper_white)

            # Combine masks
            mask_combined = mask_blue + mask_green + mask_white

            # Calculate the percentage of mask-colored pixels
            total_pixels = lower_face.shape[0] * lower_face.shape[1]
            mask_percentage = np.sum(mask_combined > 0) / total_pixels if total_pixels > 0 else 0

            # Determine mask status
            mask_status = "Mask" if mask_percentage > 0.5 else "No Mask"
            results.append({
                "bbox": (x, y, w, h),
                "status": mask_status,
                "confidence": float(mask_percentage)
            })

            # Publish the detection result via MQTT
            self.publish_mask_status(mask_status)

        return results
