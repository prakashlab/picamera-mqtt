#!/bin/bash
DIRNAME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
PIDFILENAME="startup.pid"
kill -SIGINT `cat "${DIRNAME}/${PIDFILENAME}"` && rm "${DIRNAME}/${PIDFILENAME}"
