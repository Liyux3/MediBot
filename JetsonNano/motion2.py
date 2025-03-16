#!/usr/bin/env python

import serial
import time
import sys
import paho.mqtt.client as mqtt_client

# MQTT settings
broker = 'your-mqtt-broker.example.com'
port = 1883
topic = "Fred_ELEC3848/Control"
client_id = 'Fred-O'
client_pwd = os.environ.get('MQTT_PASSWORD', '')

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Successfully connected to MQTT broker")
        else:
            print("Failed to connect, return code %d" % rc)
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.username_pw_set(client_id, client_pwd)
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client.Client):
    def on_message(client, userdata, msg):
        command = msg.payload.decode('utf-8')
        print("Received MQTT message:", command)
        
        # Send the command to the Arduino via the serial port
        # Ensure that ser is defined globally
        try:
            ser.write((command + "\n").encode())  # Appending newline if necessary
            print("Sent command to serial:", command)
        except Exception as e:
            print("Failed to send command via serial:", e)
    client.subscribe(topic)
    client.on_message = on_message


# --- Configuration ---
SERIAL_PORT = '/dev/ttyUSB0'  # Change to your Arduino serial port
BAUD_RATE = 115200

# --- Main Code ---
ser = None
print("--- Arduino Serial Commander ---")
print("Enter commands like 'W:0.5', 'A:0.2', 'S', etc.")
print("Type 'quit' or press Ctrl+C to exit.")
print("-" * 30)

# --- Connect to Serial Port ---
print("Connecting to %s at %d baud..." % (SERIAL_PORT, BAUD_RATE))
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
except Exception as e:
    print("Failed to open serial port:", e)
    sys.exit(1)
time.sleep(2)  # Wait for Arduino to reset after connection
if ser.is_open:
    print("Connected successfully!")
else:
    print("Failed to open serial port.")
    sys.exit(1)

# Connect to MQTT broker and subscribe to the topic
mqtt_client_instance = connect_mqtt()
subscribe(mqtt_client_instance)
mqtt_client_instance.loop_start()  # Runs network handling in a background thread

try:
    while True:
        # You can optionally add code here to read from serial, etc.
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    if ser:
        ser.close()
    mqtt_client_instance.loop_stop()

