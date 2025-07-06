#!/bin/bash
echo 'FILMMAKERS DREAM' | tr '\n' ' ' > /dev/shm/interface
echo 'Gonzo Pi v.' | tr '\n' ' ' > /dev/shm/vumeter
cat VERSION | tr '\n' ' ' >> /dev/shm/vumeter
#cd ./gui
#./tarinagui.bin
cd /home/pi/gonzopi/gui
sudo python3 gonzopi_menu.py
