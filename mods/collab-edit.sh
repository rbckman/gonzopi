#!/bin/sh
# TARINA COLLABORATION EDIT
# $1 filmtitle
# $2 filename
PATH=`pwd`

/usr/bin/rsync --rsh='/usr/bin/ssh -p 18888' -avr -P /home/pi/Videos/$1 tarina@tarina.org:/home/tarina/Videos --delete
