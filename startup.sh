#!/bin/bash
DIRNAME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
PIDFILENAME="startup.pid"
/usr/bin/python3 "${DIRNAME}/mqtt_illumination.py" -c > "${DIRNAME}/startup.log" &
PID=$!
echo $PID > "${DIRNAME}/${PIDFILENAME}"
