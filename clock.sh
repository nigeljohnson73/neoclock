#!/bin/sh

while [ 1 ]; do
	echo "Starting python LEDClock"
	cd /home/pi/neoclock
	. /home/pi/.env/bin/activate
	python clock.py
	echo "LEDClock stopped, restarting"
	sleep 1
done
