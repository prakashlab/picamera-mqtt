# pac-hand-hygiene-intervention
Alert system prototype for the Stanford PAC Hand Hygiene Intervention Project.
This software needs to be run from a Raspberry Pi.

## Hardware Setup
Connect a NeoPixel Stick to the Raspberry Pi as follows:

- Connect VIN of the NeoPixel Stick to the 3.3V power pin of the Raspberry Pi
- Connect GND of the NeoPixel Stick to a GND pin of the Raspberry Pi
- Connect DIN of the NeoPixel Stick to pin 18 (PWM0) of the Raspberry Pi

## Software Setup
Clone this repo, for example with:
```
cd
mkdir hand-hygiene
cd hand-hygiene
git clone https://github.com/ethanjli/pac-hand-hygiene-intervention.git intervention
```
Install required dependencies from `requirements.txt`, for example with:
```
cd ~/hand-hygiene/intervention
sudo pip3 install -r requirements.txt
```
You will have to blacklist the Broadcom audio kernel module, for example as follows:
```
sudo sh -c 'echo "blacklist snd_bcm2835" > /etc/modprobe.d/blacklist-sound.conf'
```
Then confirm that everything works correctly by running the `sticktest.py` script with
root privileges, as follows:
```
cd ~/hand-hygiene/intervention
sudo python3 intervention_client/sticktest.py -c
```
Note that the `-c` command-line flag instructs the script to turn off all LEDs when
the script quits.

## Deployment Setup

### Config File
You will need to have a USB drive handy. It will need to have a `settings.json` file
in the root of the drive. For an example, refer to the `config/settings.json` file.
You will need to set up USB automount so that the Raspberry Pi can read the
config file from the USB drive:
```
cd ~/hand-hygiene/intervention
sudo apt-get install usbmount
sudo cp -r systemd/systemd-udevd.service.d /etc/systemd/system/
```
You may need to restart the Raspberry Pi after setting up USB automount.
You should confirm that you can see a file at `/media/usb0/settings.json`.
Next, you will need to generate a keyfile at `~/hand-hygiene/settings.key`
to encrypt the config file, and then encrypt the config file:
```
cd ~/hand-hygiene/intervention
python3 -m intervention_client.tools.generate_key
```
Next, you will need to encrypt the settings file using your key to generate a
file at `/media/usb0/settings_encrypted.json`:
```
cd ~/hand-hygiene/intervention
sudo python3 -m intervention_client.tools.encrypt_config
```
Finally, you should copy the `settings.key` keyfile and the unencrypted `settings.json`
file to somewhere for safe-keeping. You may want to copy the `settings.key` file onto the
USB drive, remove the USB drive from the Raspberry Pi, copy the `settings.key` and
`settings.json` files to somewhere else on another computer. Then, for security, you should
delete the `settings.key` and `settings.json` files from the USB drive - otherwise, an
attacker can read the settings by stealing the USB drive.

If you ever need to update the config settings of the network connection, you can
edit your `settings.json` file on a separate computer (e.g. another Raspberry Pi), then 
encrypt it to a `settings_encoded.json` file at a path you set:
```
cd ~/hand-hygiene/intervention
vim /path/to/settings.json
python3 -m intervention_client.tools.encrypt_config --input /path/to/settings.json --key /path/to/settings.key --output /path/to/settings_encoded.json
```
Then you can shut down the Raspberry Pi running the client, remove the USB drive,
copy the new `settings_encoded.json` file onto the USB drive to overwrite it, and
plug the USB drive back into the Raspberry Pi and start it back up.


### Autostart
These instructions assume that the username of the default user on the Raspberry Pi has
been changed from `pi` to `pac`.
To automatically run the prototype when the Raspberry Pi starts up, install the
`mqtt_illumination.service` systemd unit:
```
cd ~/hand-hygiene/intervention
sudo cp systemd/mqtt_illumination.service /etc/systemd/system/mqtt_illumination.service
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

### MQTT Server Setup

### Physical Security
To prevent the Raspberry Pi's SD card from being removed so that an attacker can read the keyfile
on the SD card without knowing the login credentials of the Raspberry Pi, either superglue the SD
card into the Raspberry Pi board or pot it with epoxy.

### Mounting
