#!/bin/bash
DIRNAME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
PIDFILENAME="startup.pid"
STARTWAIT=5

cd "${DIRNAME}"
/usr/bin/python3 -m intervention_client.mqtt_illumination > "${DIRNAME}/startup.log" &
PID=$!
echo $PID > "${PIDFILENAME}"
