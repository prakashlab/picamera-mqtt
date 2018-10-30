#!/bin/bash
DIRNAME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
PIDFILE="/var/run/mqtt_illumination.pid"
STARTWAIT=5

cd "${DIRNAME}"
/usr/bin/python3 -m intervention_client.mqtt_illumination > "${DIRNAME}/startup.log" &
PID=$!
echo $PID > "${PIDFILE}"
