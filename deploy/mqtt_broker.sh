#!/bin/bash
DIRNAME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
CONFNAME="broker.conf"

cd "${DIRNAME}"
mosquitto -c "config/${CONFNAME}"
