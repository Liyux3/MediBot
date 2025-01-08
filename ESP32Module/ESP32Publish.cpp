/*

Upload this script to the ESP32 board

File name: ESP32Publish.cpp
Description: Enable ESP32 to connect to the WiFi network and publish messages to a MQTT broker
Version: Draft (Not tested)

This is a modified version of code from https://www.emqx.com/en/blog/esp32-connects-to-the-free-public-mqtt-broker
*/


#include <WiFi.h>
#include <PubSubClient.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

const int sda_pin = 4;
const int scl_pin = 5;

Adafruit_BME280 bme; // Data Transfer in I2C protocol


// WiFi
const char *ssid = "ELEC3848"; // Enter your Wi-Fi name
const char *password = "";  // Set your WiFi password  // Enter Wi-Fi password

// MQTT Broker
const char *mqtt_broker = "broker.emqx.io";
const char *topic = "Fred_ELEC3848/SayHello";
const char *mqtt_username = "Fred-O"; // May need to change later
const char *mqtt_password = "";  // Set your MQTT password // May need to change later
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
    // Set software serial baud to 115200;
    Serial.begin(115200);
    // Connecting to a WiFi network
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.println("Connecting to WiFi..");
    }
    Serial.println("Connected to the Wi-Fi network");
    //connecting to a mqtt broker
    client.setServer(mqtt_broker, mqtt_port);
    client.setCallback(callback);
    while (!client.connected()) {
        String client_id = "esp32-client-";
        client_id += String(WiFi.macAddress());
        Serial.printf("The client %s connects to the public MQTT broker\n", client_id.c_str());
        if (client.connect(client_id.c_str(), mqtt_username, mqtt_password)) {
            Serial.println("Public EMQX MQTT broker connected");
        } else {
            Serial.print("failed with state ");
            Serial.print(client.state());
            delay(2000);
        }
    }
    // Publish and subscribe
    client.publish(topic, String("First msg is temp: ", bme.readTemperature()));
    client.subscribe(topic);
}

void callback(char *topic, byte *payload, unsigned int length) {
    Serial.print("Message arrived in topic: ");
    Serial.println(topic);
    Serial.print("Message:");
    for (int i = 0; i < length; i++) {
        Serial.print((char) payload[i]);
    }
    Serial.println();
    Serial.println("-----------------------");
}

void loop() {
    client.loop();
}
