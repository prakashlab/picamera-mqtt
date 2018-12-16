#!/bin/bash
DIRNAME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
PIDFILE="/var/run/mqtt_imaging.pid"

cd "${DIRNAME}"
./stop_mqtt_imaging.sh
cd ..
/usr/bin/python3 -m picamera_mqtt.imaging.mqtt_client_camera &
PID=$!
sudo bash -c "echo $PID > $PIDFILE"
