#!/bin/sh
path="/home/jetson/Documents/droneCode/optical_guidance_system/jetson_code/JetsonLoop.py"
echo "Running script: $path"
echo "jetson" | sudo -S python2 $path
echo "Press any key to continue"
while [ true ] ; do
	read -n 1
	if [ $? = 0 ] ; then
		exit
	fi
done
