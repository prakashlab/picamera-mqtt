# pac-hand-hygiene-intervention
Alert system prototype for the Stanford PAC Hand Hygiene Intervention Project.
This software needs to be run from a Raspberry Pi.

## MQTT Broker Server Setup

To run the MQTT broker server, edit `deploy/config/broker.conf` and then run
`deploy/mqtt_broker.sh`.

## Client Deployment Setup

These instructions are for setting up a Raspberry Pi to deploy a visual alert client.

### Preparation

You will need to install some packages on the Raspberry Pi, as follows:
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install git python3-pip
sudo apt-get install vim byobu wicd-curses # optional, but makes your life easier
```

You will need to use the `raspi-config` tool to change the password of the pi user,
set the locale to `en_US UTF-8`, set the keyboard layout to `English (US)`,
change the hostname of the Raspberry Pi, and set the Raspberry Pi to wait for an
internet connection upon startup.

You will need to edit the `/etc/wpa_supplicant/wpa_supplicant.conf` configuration
file to connect to wi-fi if you are deploying the Raspberry Pi with a Wi-Fi connection.

For security, you should change the username of the pi user to something else.
This will involve temporarily enabling the `root` account and using `usermod`. For example,
to change it to `pac`:
```
# log in as pi, then:
sudo passwd -l root # set a password for the root account to enable it!
logout # log out of the pi account!
# then log in as root, using the password you just set, then:
usermod -l pac pi # rename the pi account to pac!
usermod -m -d /home/pac pac # rename the pi home folder!
logout # log out of the pac account!
# then log in as pac, then:
sudo passwd -l root # set an empty password for the root account to disable it!
```

You will need to have a USB drive handy. It will need to have a `settings.json` file
in the root of the drive. For an example file, refer to `deploy/config/settings_cloudmqtt.json`.
The `pi_username` parameter in the `settings.json` file should match the username
of the pi user on the Raspberry Pi.

### Client Hardware Setup
Connect a NeoPixel Stick to the Raspberry Pi as follows:

- Connect VIN of the NeoPixel Stick to the 3.3V power pin of the Raspberry Pi
- Connect GND of the NeoPixel Stick to a GND pin of the Raspberry Pi
- Connect DIN of the NeoPixel Stick to pin 18 (PWM0) of the Raspberry Pi

### Client Software Setup
Clone this repo, for example with:
```
cd
mkdir hand-hygiene
cd hand-hygiene
git clone https://github.com/ethanjli/pac-hand-hygiene-intervention.git intervention
```
Install required dependencies from `requirements_deployment.txt`, for example with:
```
cd ~/hand-hygiene/intervention
sudo pip3 install -r requirements_deployment.txt
```
You will have to blacklist the Broadcom audio kernel module, for example as follows:
```
sudo sh -c 'echo "blacklist snd_bcm2835" > /etc/modprobe.d/blacklist-sound.conf'
```
Then confirm that everything works correctly by running the `sticktest.py` script with
root privileges, as follows:
```
cd ~/hand-hygiene/intervention
sudo python3 -m intervention_system.tests.illumination.stick_patterns
```

### Client Config
You will need to set up USB automount so that the Raspberry Pi can read the
config file from the USB drive you set up previously:
```
cd ~/hand-hygiene/intervention
sudo apt-get install usbmount
sudo cp -r deploy/systemd/systemd-udevd.service.d /etc/systemd/system/
```
You may need to restart the Raspberry Pi after setting up USB automount.
You should confirm that you can see a file at `/media/usb0/settings.json`.

Next, you will need to generate a keyfile at
`~/hand-hygiene/intervention/deploy/settings.key`, for file encryption:
```
cd ~/hand-hygiene/intervention
python3 -m intervention_system.tools.config.generate_key
```

Next, you will need to encrypt the `settings.json` file using your key, to generate a
file at `/media/usb0/settings_encrypted.json`:
```
cd ~/hand-hygiene/intervention
sudo python3 -m intervention_system.tools.config.encrypt_config
```

Finally, you should copy the `settings.key` keyfile and the unencrypted `settings.json`
file to somewhere for safe-keeping. You may want to copy the `settings.key` file onto the
USB drive, remove the USB drive from the Raspberry Pi, copy the `settings.key` and
`settings.json` files to somewhere else on another computer. Then, for security, you should
delete the `settings.key` and `settings.json` files from the USB drive - otherwise, an
attacker can read the settings by stealing the USB drive.

If you ever need to update the config settings of the network connection, you can
edit your `settings.json` file on a separate computer (e.g. another Raspberry Pi), then 
encrypt it to a `settings_encrypted.json` file at a path you set:
```
cd ~/hand-hygiene/intervention
vim /path/to/settings.json
python3 -m intervention_system.tools.encrypt_config --input /path/to/settings.json --key /path/to/settings.key --output /path/to/settings_encrypted.json
```

Then you can shut down the Raspberry Pi running the client, remove the USB drive,
copy the new `settings_encrypted.json` file onto the USB drive to overwrite it, and
plug the USB drive back into the Raspberry Pi and start it back up.


### Client Software Autostart
These instructions assume that the username of the default user on the Raspberry Pi has
been changed from `pi` to `pac`.
To automatically run the prototype when the Raspberry Pi starts up, install the
`mqtt_illumination.service` systemd unit:
```
cd ~/hand-hygiene/intervention
sudo cp deploy/systemd/mqtt_illumination.service /etc/systemd/system/mqtt_illumination.service
sudo systemctl enable mqtt_illumination
```
You can manually start the service with systemd, view the status of the service with systemd,
view its output logs with journalctl, or kill the script with systemd:
```
sudo systemctl start mqtt_illumination
systemctl status mqtt_illumination
journalctl -u mqtt_illumination
sudo systemctl stop mqtt_illumination
```

### Physical Security
To prevent the Raspberry Pi's SD card from being removed so that an attacker can read the keyfile
on the SD card without knowing the login credentials of the Raspberry Pi, either superglue the SD
card into the Raspberry Pi board or pot it with epoxy.

### Mounting
TODO

## System Administration

You can remotely send deployment management commands to the Raspberry Pi client
by sending messages over the `deployment` topic. The
`intervention_system/tools/deploy/mqtt_send_deployment` script lets you do this
from the command-line, as follows:
```
cd ~/hand-hygiene/intervention
python3 -m intervention_system.tools.deploy.mqtt_send_deployment shutdown # shut down the Raspberry Pi
python3 -m intervention_system.tools.deploy.mqtt_send_deployment reboot # reboot the Raspberry Pi
python3 -m intervention_system.tools.deploy.mqtt_send_deployment stop # stop the illumination client
python3 -m intervention_system.tools.deploy.mqtt_send_deployment restart # restart the illumination client
python3 -m intervention_system.tools.deploy.mqtt_send_deployment "git pull" # update the repo and restart the illumination client
```
