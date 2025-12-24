#!/bin/bash
echo 'Setting your wifi region'
sudo iw reg set US
sudo iw dev wlan0 set power_save off
