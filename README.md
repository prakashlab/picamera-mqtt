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
These instructions assume that the username of the default user on the Raspberry Pi has
been changed from `pi` to `pac`.
You will need to set up usb automount:
```
cd ~/hand-hygiene/intervention
sudo apt-get install usbmount
sudo cp -r systemd/systemd-udevd.service.d /etc/systemd/system/
```
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
