#!/bin/bash
DIRNAME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
PIDFILENAME="startup.pid"

if [ -f "${DIRNAME}/${PIDFILENAME}" ]; then
	kill -SIGINT `cat "${DIRNAME}/${PIDFILENAME}"` && rm "${DIRNAME}/${PIDFILENAME}"
fi
