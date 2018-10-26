#!/bin/bash
DIRNAME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
PIDFILENAME="startup.pid"
STARTWAIT=5

cd "${DIRNAME}"
/bin/bash "cancel_startup.sh" # Quit the script started in startup_breathe.sh
/usr/bin/python3 -m intervention_client.mqtt_illumination > "${DIRNAME}/startup.log" &
PID=$!
echo $PID > "${PIDFILENAME}"
