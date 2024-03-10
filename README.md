Gonzo Pi
=============
### a reboot of filmmaking

The camera that runs Linux with an unique all-in-one filmmaking interface. Shooting your videos as takes in a scene and shot based structure. Gonzo Pi is 3d printed, easy to mod & repair.

![Gonzopi](/extras/gonzopi-01.jpeg)

Software
--------
- film mode & picture mode, soon music video mode.
- glue selected clips together and/or cutting them by setting in & out points easily.
- making timelapses, stop-motion, voiceover, music track recording, slo-mo recording, fast-forward recording
- cut and copy and move clips around
- backup to usb harddrive or your own server
- upload or stream to youtube or your own server
- auto correction can easily be switched on or off for shutter, iso and colors so *operator* is in full control also for audio levels
- connect many GonzoPis together for multicamera shooting
- stream a film a take or a scene through the network
- control the camera with silent physical buttons or a usb-wireless-keyboard or through a built in apache2 web server or ssh or ports, you choose how to go gonzo just the way you like it

### GUI
![Gonzopi](/extras/gonzopi-02.jpeg)

### Buttons
![Gonzopi](/extras/gonzopi-04.jpeg)
![Buttons](/extras/buttons.png)

#### in view mode
![Buttons](/extras/view-buttons.png)

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

![Gonzopi](/extras/gonzopi-03.jpeg)

more about Gonzo Pi here [https://github.com/rbckman/gonzopi_build](https://github.com/rbckman/gonzopi_build)

No, need to build custom case, or buttons, this will work with a Raspberry Pi and any of it's camera modules, usb keyboards and usb audio cards, a regular hdmi display should also be fine.

If you want to build it, there's a complete guide here [https://github.com/rbckman/gonzopi_build/blob/master/gonzopi-manual.md#building-repairing-and-modding](https://github.com/rbckman/gonzopi_build/blob/master/gonzopi-manual.md#building-repairing-and-modding)

If you want to order a prebuilt device contact go(at)gonzopi.org (only preorders now)

Connect
-------
Matrix [#tarina:matrix.tarina.org](https://riot.im/app/#/room/#tarina:matrix.tarina.org)

Mail rob(at)gonzopi.org

