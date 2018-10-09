#!/bin/bash
DIRNAME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
PIDFILENAME="startup.pid"
echo $DIRNAME
/usr/bin/python3 "${DIRNAME}/sticktest.py" -c | tee "${DIRNAME}/startup.log" &
PID=$!
echo $PID > "${DIRNAME}/${PIDFILENAME}"
