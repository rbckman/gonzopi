#!/bin/bash
echo 'Gonzo Pi v.' | tr '\n' ' ' > /dev/shm/vumeter
cat VERSION | tr '\n' ' ' >> /dev/shm/vumeter
#cd ./gui
#./tarinagui.bin
cd ./gui
sudo python3 gonzopi_menu.py
