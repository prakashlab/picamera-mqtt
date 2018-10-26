#!/bin/bash
DIRNAME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
PIDFILENAME="startup.pid"

cd "${DIRNAME}"
/usr/bin/python3 -m intervention_client.stickbreathe > /dev/null &
PID=$!
echo $PID > "${DIRNAME}/${PIDFILENAME}"

