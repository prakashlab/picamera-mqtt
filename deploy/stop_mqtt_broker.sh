#!/bin/bash
PIDFILE="/var/run/mqtt_broker.pid"

if [ -f "${PIDFILE}" ]; then
	kill -SIGINT `cat "${PIDFILE}"` && sudo rm "${PIDFILE}"
fi
