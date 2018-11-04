#!/bin/bash
PIDFILE="/var/run/mqtt_illumination.pid"

if [ -f "${PIDFILE}" ]; then
	kill -SIGINT `cat "${PIDFILE}"` && rm "${PIDFILE}"
fi
