#!/bin/bash
# Basic if statement
version="$(lsb_release -c -s)"
echo $version
if [ "$version" = "buster" ]
then
    echo "Debian Buster found"
else
    echo "Debian Stretch found"
fi
