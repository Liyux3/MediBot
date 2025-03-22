#Upload this script to Jetson Nano, and run as background program

# JSON message format:
# {"Type": "Play_Music", "Name":String, "Enable":boolean}


import pygame
import time
import paho.mqtt.client as mqtt
import json
import os
import threading

pygame.mixer.init()


path = 'audio'
music_list = []

for song in os.listdir(path):
    music_list.append(song)


# MQTT broker settings
broker = "broker.emqx.io"
port = 1883
topic = "Fred_ELEC3848/SayHello"
client_id = "JetsonNano"

client = mqtt.Client()
client.connected_flag = False 

def Play_Music(path):
    pygame.mixer.music.load(path)
    # Play the music repeatedly (infinite loop)
    pygame.mixer.music.play(loops=-1)
    print("Playing in loop")
    # Wait until the music finishes playing
    while pygame.mixer.music.get_busy():
        time.sleep(1)


# Callback for when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
        client.connected_flag = True
    else:
        print(f"Connection failed with code {rc}")
        client.connected_flag = False

# Callback for when the client disconnects
def on_disconnect(client, userdata, rc):
    print(f"Disconnected with code {rc}")
    client.connected_flag = False

def on_message(client, userdata, msg):
    print("Got message")
    payload = msg.payload.decode()
    print(payload)
    demsg = json.loads(payload)
    if demsg["Type"] == "Play_Music":
        target_song = demsg["Name"]
        enable = demsg["Enable"]
        tpath = os.path.join('audio', target_song)
        print(tpath)
        if enable:
            try:
                # Start playing the music in a new thread
                threading.Thread(target=Play_Music, args=(tpath,)).start()
            except FileNotFoundError:
                print("No such song")
        else:
            # Stop playing any currently playing music
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                print("Music stopped by command")
    return
    

# Assign callbacks
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

client.connect(broker, port)
client.subscribe(topic)
client.loop_start()  # Runs network handling in a background thread

try: 
    while True:
        if client.connected_flag:
            time.sleep(1)
except KeyboardInterrupt:
    print("Interrupted by user")
finally:
    client.disconnect()
    client.loop_stop()
