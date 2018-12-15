#!/bin/bash
DIRNAME="/home/pi/Desktop/picamera-mqtt/"
PIDFILE="/var/run/mqtt_imaging.pid"

cd "${DIRNAME}"
/usr/bin/python3 -m picamera_mqtt.imaging.mqtt_client &
PID=$!
echo $PID > "${PIDFILE}"
