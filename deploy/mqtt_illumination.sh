#!/bin/bash
DIRNAME="/home/pac/hand-hygiene/intervention/"
PIDFILE="/var/run/mqtt_illumination.pid"
STARTWAIT=5

cd "${DIRNAME}"
/usr/bin/python3 -m intervention_system.clients.mqtt_illumination &
PID=$!
echo $PID > "${PIDFILE}"
