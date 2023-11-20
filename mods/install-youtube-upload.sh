#!/bin/bash

# Install script for youtube upload mod
# https://github.com/tokland/youtube-upload

ROOT_UID=0   # Root has $UID 0.

if [ "$UID" -eq "$ROOT_UID" ]
then
   echo "OK"
else
    echo "Run with sudo!"
    exit 0
fi

echo "INSTALLING AND ENABLING MOD: youtube-upload"

sudo pip3 install --upgrade google-api-python-client oauth2client progressbar2

echo "youtube-upload" >> mods-enabled
