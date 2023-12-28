Gonzo Pi
=============

<<<<<<< HEAD
Go Gonzo with the Ultimate Filmmaking Device!
How to build and use it here [https://github.com/rbckman/gonzopi_build](https://github.com/rbckman/gonzopi_build)
=======
Turn a Raspberry Pi to the Ultimate Filmmaking Device!

Demonstration of the device here [https://github.com/rbckman/gonzopi_build](https://github.com/rbckman/gonzopi_build)

No, need to build custom case, or buttons, this will work with a Raspberry Pi and any of it's camera modules, usb keyboards and usb audio cards, a regular hdmi display should also be fine.

If you want to build it, there's a complete guide here [https://github.com/rbckman/gonzopi_build/blob/master/gonzopi-manual.md#building-repairing-and-modding](https://github.com/rbckman/gonzopi_build/blob/master/gonzopi-manual.md#building-repairing-and-modding)

If you want to order a prebuilt device contact go(at)gonzopi.org (only preorders now)
>>>>>>> 32c849051bc25683e63d0f3dc05db5d2835d809e

Software
--------
- glue selected clips together and/or cutting them.
- making timelapses, stop-motion, voiceover, music track recording, slo-mo recording, fast-forward recording
- cut and copy and move clips around
- backup to usb harddrive or your own server
- upload or stream to youtube or your own server
- auto correction can easily be switched on or off for shutter, iso and colors so *operator* is in full control also for audio levels
- connect many GonzoPis together for multicamera shooting
- stream a film a take or a scene through the network
- control the camera with silent physical buttons or a usb-wireless-keyboard or through a built in apache2 web server or ssh or ports, you choose how to go gonzo just the way you like it

### GUI
![GUI](/extras/gonzopi-gui.jpeg)

### Buttons
![Buttons](/extras/buttons.png)

Installing
----------
Download [Raspbian buster (not the latest!)](https://www.raspberrypi.org/downloads/raspbian/) and follow [install instructions | a simple install script should take care of it all!](https://www.raspberrypi.org/documentation/installation/installing-images/README.md).
[Ssh into](https://www.raspberrypi.org/documentation/remote-access/ssh/) Raspberry Pi and run:
```
sudo apt-get install git
```
Go to /home/pi/ folder
```
cd /home/pi
```
Git clone Gonzo Pi and then run install script with sudo:
```
git clone https://github.com/rbckman/gonzopi.git
cd gonzopi
sudo ./install.sh
```
You'r ready to go gonzo! 
```
python3 gonzopi.py
```

Connect
-------
Matrix [#tarina:matrix.tarina.org](https://riot.im/app/#/room/#tarina:matrix.tarina.org)

Mail rob(at)gonzopi.org

