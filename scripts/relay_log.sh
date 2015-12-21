#!/bin/bash
#DATETIME=`date -u +%Y%m%d_%H%M%S.%N_UTC`
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
DATETIME=`date +%Y%m%d`
FILENAME=$DATETIME'_relay_daemon.log'
echo $FILENAME
cp /var/log/upstart/relay_daemon.log /mnt/log/relay/$FILENAME
chmod 666 /mnt/log/relay/$FILENAME
