#!/bin/bash

ROOT_UID=0   # Root has $UID 0.

if [ "$UID" -eq "$ROOT_UID" ]
then
   echo "OK"
else
    echo "Run with sudo!"
    echo "sudo ./restorebak.sh"
    exit 0
fi

while true; do
    read -p "Undo rpi-update? [y]es or [n]o?" yn
    case $yn in
        [Yy]* ) echo "Restoring from backup now..."
cp -r /boot.bak/* /boot/
cp -r /lib/modules.bak/* /lib/modules/
            break;;
        [Nn]* ) echo "Yes, sir! we are done!";break;;
        * ) echo "Please answer yes or no.";;
    esac
done

