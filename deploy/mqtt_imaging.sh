#!/bin/bash
DIRNAME="/home/pi/Desktop/picamera-mqtt/"

cd "${DIRNAME}"
/usr/bin/python3 -m picamera_mqtt.imaging.mqtt_client_camera
