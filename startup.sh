#!/bin/bash
DIRNAME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
PIDFILENAME="startup.pid"
STARTWAIT=5

_IP=$(hostname -I) || true
if [ "$_IP" ]; then
  printf "Network connection confirmed. IP address: %s\n" "$_IP"
else
  echo "Restarting dhcpcd to try to establish network connection..."
  sudo systemctl daemon-reload
  sudo systemctl restart dhcpcd
  _IP=$(hostname -I) || true
  if [ "$_IP" ]; then
    printf "Network connection confirmed. IP address: %s\n" "$_IP"
  else
    echo "Network connection could not be established! Quitting..."
    exit 1
  fi
fi
/bin/bash "${DIRNAME}/cancel_startup.sh" # Quit the script started in startup_breathe.sh
/usr/bin/python3 "${DIRNAME}/mqtt_illumination.py" > "${DIRNAME}/startup.log" &
PID=$!
echo $PID > "${DIRNAME}/${PIDFILENAME}"
