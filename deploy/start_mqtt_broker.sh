#!/bin/bash
DIRNAME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
CONFNAME="broker.conf"
PIDFILE="/var/run/mqtt_broker.pid"

cd "${DIRNAME}"
./stop_mqtt_broker.sh
mosquitto -c "config/${CONFNAME}" &
PID=$!
sudo bash -c "echo $PID > $PIDFILE"
