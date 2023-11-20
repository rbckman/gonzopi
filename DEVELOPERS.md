DEVELOPERS
==========

If you want to join me in this journey to make the best open filmmaking camera please do not hesitate to contact me on features.

Teh best way to develop is using screen in terminal and starting tarina in one window then you'll get debug messages directly in that window.

THINGS
======

Notes to myself as I'm the only developer at teh moment.
-Rob

Quality / Usability
-------------------

Found a sweet spot between usability and quality (23), bitrate (5 mb/s)
This produces about 25 mb per minute. The convertion to mp4 format does not feel so slow anymore likewise the compiling of the film. This is good stuff.

Image sensors
-------------

There's plenty of image sensors for the Raspberry Pi to choose from, I want to support as many sensors I can. Currently though you need to change your sensor in tarina.py, search for 'ov5' and you'll find where to select. They all have different oscillators so the framerate varies pretty much. But when you get it right the sound will be in sync. Will make a tarina config file in home folder so when you start tarina interface for the first time it will ask you about your sensor.

Cancel renderer
---------------

This is a must feature, and I sort of know how to implement it.

Viewfinder for 3.5 inch screen
------------------------------

There's no such thing to buy so I had to make a viewfinder myself, took a while before I found the right convex lens but I have it now. It works with magnet snap on. Really, really usefull! will write it in the manual as a addon thing...

How to update alsa-tools arecord
=================================

The vumeter comes directly from alsa-tools arecord, it's just modified so it writes the vumeter directly to /dev/shm/vumeter. If you need to update alsa-tools here's how:

You need to be able to build alsa-utils from source
enable dev-src in /etc/apt/sources.list

```
apt source alsa-utils
cd alsa-utils*
sudo apt update
sudo apt install libncurses5-dev
sudo apt install libasound2-dev
./configure
make
cd aplay
make
make arecord
```


Ecasound update
===============

### Python example

```
from pyeca import *
e = ECA_CONTROL_INTERFACE()
e.command("cs-add chainsetup")
e.command("c-add 1st_chain")
e.command("ai-add plughw,0,0 ")
e.command("ao-add /dev/dsp")
e.command("cop-add -efl:100")
e.command("cop-select 1")
e.command("copp-select 1")
e.command("cs-connect")
e.command("start")
```

### Ecasound config file

```
# ecasound chainsetup file

# general 
-B:rtlowlatency -n:"write_chain" -X -z:noxruns -z:nopsr -z:mixmode,sum

# audio inputs 
-a:1chain,2chain -f:s16_le,2,44100 -i:alsahw,3,0,0

# audio outputs 
-a:1chain -f:s16_le,2,44100 -o:alsahw,3,0,0
-a:2chain -f:s16_le,2,44100 -o:test.wav,
```
