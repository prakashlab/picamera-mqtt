#!/bin/bash
DIRNAME="/home/pac/hand-hygiene/intervention/"
PIDFILE="/var/run/mqtt_illumination.pid"

cd "${DIRNAME}"
/usr/bin/python3 -m intervention_system.illumination.mqtt_client &
PID=$!
echo $PID > "${PIDFILE}"
