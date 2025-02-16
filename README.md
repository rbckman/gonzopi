Gonzo Pi
=============
### Filmmakers dream

a 3d printed FOSS digital video camera with the essential filmmaking tools. 

![Gonzopi](/extras/gonzopi-01.jpeg)

Features
--------

The most innovative feature is that you film in a scene, shot and take based structure. You can put placeholders in for shots or scenes that need to be filmed later on. When *view button* is pressed while a scene is selected Gonzo Pi will glue all the last takes of all the shots in that scene together and then play it! Press view while film is selected will glue all scenes together and play your film!

Gluing takes and scenes together takes a while and depends on your usb harddrive speed and the video bitrate. It also depends what Raspberry Pi you drive Gonzo Pi with. I have successfully been making films with 3B, 3B+ and 4B. I recommend 4B as the wifi and USB speed is much faster. Default bitrate for video is 8.888 Mb/s and sound is recorded uncompressed as 48khz wav before it is muxed together into a mp4 video.

- edit takes by setting in & out points easily in-camera (will reglue your scene and film if new edits found)
- add voiceover and/or music tracks with dubbing feature
- adjustable framerates for slo-mo recording or fast-forward recording
- work on many films, move and copy shots or scenes from film to film. (USB to USB drive)
- live stream to another device in the same network
- multicamera mode lets you control many Gonzo Pis in the same network, and sync footage between (makes live multicamera work easy as down to couple of buttons)
- of course manual or auto shutter, iso and white balance
- a vu meter for the incoming sound while recording
- change audio levels while recording
- control Gonzo pi with silent physical buttons or a usb-wireless-keyboard or through the built-in apache2 web server or over ssh or ports, you choose how to go gonzo just the way you like it
- Isaac879 3-Axis Camera Slider support https://www.thingiverse.com/thing:4547074 (plug and play, slider is controlled from Gonzo Pi Gui)
- timelapse mode
- set beep (countdown in x seconds before filming)
- set take lenght (min 0.2 s max unlimited)
- video effects (negative, solarize, denoise, colorpoint, colorswap, posterize, blur, film)
- blend modes (screen, average, darken, lighten, burn, multiply)

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

