#!/bin/bash
DIRNAME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
CONFNAME="broker.conf"

cd "${DIRNAME}"
cd ..
python3 -m picamera_mqtt.tests.mqtt_clients.mock_host --config settings_localhost.json
