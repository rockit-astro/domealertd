# DomeAlert Server

Part of the observatory software for the Warwick one-meter, NITES, and GOTO telescopes.

`domealertd` is a Pyro server that runs on the DomeAlert units to provide a [roomalertd](https://github.com/warwick-one-metre/roomalertd) compatible replacement for the previous RoomAlert units.


### Installing
Start by adding `dtoverlay=w1-gpio` to `/boot/config.txt` and reboot to enable the onewire bus.

Install dependencies and server with:
```
sudo apt install git python3-setuptools python3-jsonschema python3-pyro4 python3-rpi.gpio
git clone https://github.com/warwick-one-metre/roomalertd.git
sudo python3 setup.py install
```

Activate server by running:
```
sudo systemctl enable domealertd@<device>
```
and then rebooting, where `[device]` is the name of the configuration to run, with matching json file (e.g. `onemetre`).