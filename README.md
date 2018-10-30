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
To automatically run the prototype when the Raspberry Pi starts up, add a call to the
`startup.sh` script to `/etc/rc.local`, for example by adding the following lines before
the last `exit 0` line of `/etc/rc.local`:
```
./home/pac/hand-hygiene/intervention/startup.sh
```
You can also copy the `rc.local` script, which also has a few lines for printing
additional information upon startup, as follows:
```
cd ~/hand-hygiene/intervention
sudo cp rc.local /etc/rc.local
```
You can kill the script initiated from startup by running the `cancel_startup.sh` script
with root privileges, as follows:
```
./hand-hygiene/intervention/cancel_startup.sh
```
