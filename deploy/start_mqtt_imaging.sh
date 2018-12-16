#!/bin/bash
DIRNAME="/home/pi/Desktop/picamera-mqtt/"
PIDFILE="/var/run/mqtt_imaging.pid"

cd "${DIRNAME}"
./stop_mqtt_imaging.sh
/usr/bin/python3 -m picamera_mqtt.imaging.mqtt_client_camera &
PID=$!
sudo bash -c "echo $PID > $PIDFILE"
