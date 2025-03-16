import time
import paho.mqtt.client as mqtt_client
import base64
import pygame
import pygame.camera
#from PIL import Image

FPS = 2

broker = 'your-mqtt-broker.example.com'
port = 1883
topic = "Fred_ELEC3848/Picture"
client_id = 'Fred-O'
client_pwd = os.environ.get('MQTT_PASSWORD', '')

pygame.camera.init()
pygame.camera.list_cameras()
# cam = pygame.camera.Camera("/dev/video0", (640, 480))
# cam.start()

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Successfully connected to MQTT broker")
        else:
            print("Failed to connect, return code %d", rc)

    client = mqtt_client.Client()
    client.username_pw_set(username=client_id, password=client_pwd)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client):
    # raw_img = cam.get_image()
    # pygame.image.save(raw_img, 'fake_image/stream.jpg')
    #img = Image.open('fake_image/stream.jpg')
    #img.resize((128, 128))
    #img.save('fake_image/opt_stream.jpg', optimize=True, quality=10)


    with open("Thermal.jpg",'rb') as file:

        filecontent = file.read()
        encoded = base64.b64encode(filecontent)
        print(encoded)
        result = client.publish(topic,encoded,2)
    msg_status = result[0]
    if msg_status == 0:
        print(f"message sent to topic {topic}")
    else:
        print(f"Failed to send message to topic {topic}")

def main():
    client = connect_mqtt()
    client.loop_start()
    try:
        while (True):
            publish(client)
            time.sleep(1/FPS)
    except KeyboardInterrupt:
        print("Ending program")
        client.loop_stop()



main()
