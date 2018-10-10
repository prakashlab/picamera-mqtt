#!/bin/bash
DIRNAME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
PIDFILENAME="startup.pid"

/usr/bin/python3 "${DIRNAME}/stickbreathe.py" > /dev/null &
PID=$!
echo $PID > "${DIRNAME}/${PIDFILENAME}"

