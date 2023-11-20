#!/bin/sh
# TARINA COLLABORATION PULL
# $1 filmtitle
# $2 filename
PATH=`pwd`

/usr/bin/rsync -e '/usr/bin/ssh -p 18888' -avr -P tarina@tarina.org:/home/tarina/Videos/$1 /home/pi/Videos
