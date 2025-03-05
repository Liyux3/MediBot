# mask_detection.py - Using pre-trained model
import cv2
import numpy as np
import os
import json
import paho.mqtt.client as mqtt
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

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
        
        # Load the mask detector model
        self.mask_model = load_model("mask_detector.model")

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
            # Extract face ROI
            face_roi = frame[y:y+h, x:x+w]
            
            # Preprocess for the mask detector model
            face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB)
            face = cv2.resize(face, (224, 224))
            face = img_to_array(face)
            face = preprocess_input(face)
            face = np.expand_dims(face, axis=0)
            
            # Make prediction
            (mask, withoutMask) = self.mask_model.predict(face)[0]
            
            # Determine mask status
            mask_status = "Mask" if mask > withoutMask else "No Mask"
            confidence = float(mask if mask_status == "Mask" else withoutMask)
            
            results.append({
                "bbox": (x, y, w, h),
                "status": mask_status,
                "confidence": confidence
            })

            # Publish the detection result via MQTT
            self.publish_mask_status(mask_status)

        return results
