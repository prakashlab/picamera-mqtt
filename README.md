# picamera-mqtt
MQTT-based control and image capture with local and remote networked Raspberry Pi cameras.
Deployment scripts needs to be run from a Raspberry Pi. Other scripts can be run from any computer.

## MQTT Broker Server Setup

To run the MQTT broker server, edit `deploy/config/broker.conf` and then run
`deploy/mqtt_broker.sh`.

### Broker Autostart
To automatically run the MQTT broker when the host Raspberry Pi starts up,
install the `mqtt_broker.service` systemd unit:
```
cd ~/Desktop/picamera-mqtt
sudo cp deploy/systemd/mqtt_broker.service /etc/systemd/system/mqtt_broker.service
sudo systemctl enable mqtt_broker
```
You can manually start the service with systemd, view the status of the service with systemd,
view its output logs with journalctl, or kill the script with systemd:
```
sudo systemctl start mqtt_broker
systemctl status mqtt_broker
journalctl -u mqtt_broker
sudo systemctl stop mqtt_broker
```

## Camera Client Deployment Setup

These instructions are for setting up a Raspberry Pi to deploy a camera imaging client.

### Preparation
You will need to install some packages on the Raspberry Pi, as follows:
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install git python3-pip
sudo apt-get install vim byobu # optional, but makes your life easier
```

You will need to use the `raspi-config` tool to change the password of the pi user,
set the locale to `en_US UTF-8`, set the keyboard layout to `English (US)`,
change the hostname of the Raspberry Pi, and set the Raspberry Pi to wait for an
internet connection upon startup.

You will need to edit the `/etc/wpa_supplicant/wpa_supplicant.conf` configuration
file to connect to wi-fi if you are deploying the Raspberry Pi with a Wi-Fi connection.

### Client Hardware Setup
Connect a Raspberry Pi Camera to the Raspberry Pi.

### Client Software Setup
Clone this repo, for example with:
```
cd ~/Desktop
git clone https://github.com/ethanjli/picamera-mqtt.git
```
Install required dependencies from `requirements_deployment.txt`, for example with:
```
cd ~/Desktop/picamera-mqtt
sudo pip3 install -r requirements_deployment.txt
```
Then confirm that the camera works correctly by running the `capture.py` script,
as follows:
```
cd ~/Desktop/picamera-mqtt
python3 -m picamera_mqtt.tests.imaging.capture
```
This should cause the appearance of two files, `capture_pil.jpg` and
`capture_final.jpg`, in your working directory.

### Client Config
You will need to edit the `deploy/config/settings.json` config file such that:

- The `hostname` parameter is either `localhost` (if your MQTT broker is running
  on the same computer as your client) or the IP address of the computer running
  your MQTT broker.
- The `client_name` parameter and the `target_name` parameter both should say
  `camera_n`, where `n` should be replaced with a unique id number of your camera
  client. This id number will be used to uniquely label each camera stream.


### Camera Client Software Autostart
To automatically run the camera MQTT client when the Raspberry Pi starts up,
install the `mqtt_imaging.service` systemd unit:
```
cd ~/Desktop/picamera-mqtt
sudo cp deploy/systemd/mqtt_imaging.service /etc/systemd/system/mqtt_imaging.service
sudo systemctl enable mqtt_imaging
```
You can manually start the service with systemd, view the status of the service with systemd,
view its output logs with journalctl, or kill the script with systemd:
```
sudo systemctl start mqtt_imaging
systemctl status mqtt_imaging
journalctl -u mqtt_imaging
sudo systemctl stop mqtt_imaging
```

## System Tests

With an operational camera client connected to the MQTT broker server, you can run
a few tests on the computer running the MQTT broker server to confirm correct image
transfer:
```
cd ~/Desktop/picamera-mqtt
python3 -m picamera_mqtt.tests.mqtt_clients.mock_host --interval 8 --config settings_localhost.json
```

This will exercise roundtrip communication to and from the camera client with
client name `camera_1` by sending image acquisition messages to the camera client
every 8 seconds and receiving (and discarding) images captured by the camera client.

To save these images, run the following test:
```
cd ~/Desktop/picamera-mqtt
python3 -m picamera_mqtt.tools.timelapse_host --interval 15 --number 5
```
This will take a timelapse of 5 images spaced out at 15-second intervals from
all camera clients connected to the broker with client names `camera_1`, `camera_2`,
and `camera_3`; the client names queried can be changed by editing the config file.
By default, images will be saved to the `data` directory, but you can change this
with the `--output_dir` flag to specify a different path.

If you only want to capture image snapshots at a single time point, run the following test:
```
cd ~/Desktop/picamera-mqtt
python3 -m picamera_mqtt.tools.acquire_host
```
By default, images will be saved to the `data` directory, but you can change this
with the `--output_dir` flag to specify a different path. By default, images will
be saved with filenames with `acquire` at the start, but you can change this with
the `--output_prefix` flag to specify a different filename prefix.

## System Administration

You can remotely send deployment management commands to the Raspberry Pi client
by sending messages over the `deployment` topic. The
`picamera_mqtt/tools/deploy/mqtt_send_deployment` script lets you do this
from the command-line, as follows:
```
cd ~/hand-hygiene/intervention
python3 -m intervention_system.tools.mqtt_send_deployment shutdown --target_name camera_1 # shut down the Raspberry Pi running camera 1
python3 -m intervention_system.tools.mqtt_send_deployment reboot --target_name camera_1 # reboot the Raspberry Pi running camera 1
python3 -m intervention_system.tools.mqtt_send_deployment stop --target_name camera_1 # stop the illumination client running camera 1
python3 -m intervention_system.tools.mqtt_send_deployment restart --target_name camera_1 # restart the illumination client running camera 1
python3 -m intervention_system.tools.mqtt_send_deployment "git pull" --target_name camera_1 # update the repo and restart the illumination client running camera 1
```

## Camera Parameter Adjustment

You can remotely send camera parameter update commands to the Raspberry Pi client
by sending messages over the `control` topic. The
`picamera_mqtt/tools/deploy/mqtt_send_camera_params` script lets you do this
from the command-line, as follows:
```
cd ~/hand-hygiene/intervention
python3 -m intervention_system.tools.mqtt_send_camera_params --target_name camera_1 # query camera parameters from camera 1
python3 -m intervention_system.tools.mqtt_send_camera_params --target_name camera_1 --roi_zoom 1.5 # set camera zoom factor to 1.5 on camera 1
python3 -m intervention_system.tools.mqtt_send_camera_params --target_name camera_1 --shutter_speed 200 # set shutter speed to 200 ms on camera 1
python3 -m intervention_system.tools.mqtt_send_camera_params --target_name camera_1 --iso 200 # set ISO to 200 on camera 1
python3 -m intervention_system.tools.mqtt_send_camera_params --target_name camera_1 --resolution_width 1920 --resolution_height 1080 # set the image resolution to 1920x1080 on camera 1
python3 -m intervention_system.tools.mqtt_send_camera_params --target_name camera_1 --awb_gain_red 2.0 # set AWB red gain to 2.0 on camera 1
python3 -m intervention_system.tools.mqtt_send_camera_params --target_name camera_1 --awb_gain_blue 2.0 # set AWB blue gain to 2.0 on camera 1
```
Note that all camera param flags can be combined into a single command if you wish.
