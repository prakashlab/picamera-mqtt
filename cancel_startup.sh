#!/bin/bash
DIRNAME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
PIDFILE="/var/run/mqtt_illumination.pid"

if [ -f "${PIDFILE}" ]; then
	kill -SIGINT `cat "${PIDFILE}"` && rm "${PIDFILE}"
fi
