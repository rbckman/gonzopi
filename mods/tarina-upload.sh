#!/bin/sh
# TARINA.ORG MOD
# $1 filmtitle
# $2 filename
PATH=`pwd`

/usr/bin/scp -P 18888 $2 tarina@tarina.org:/home/tarina/videos/$1.mp4
