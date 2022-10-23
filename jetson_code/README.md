# Contents
 - [SITL install](#sitlInstall)
 - [Jetson Nano setup](#jetson)
 - 

<a id="sitlInstall"></a>
# SITL Simulation on desktop 
Software in the Loop (SITL) can be used to simulate Ardupilot. it can be used for a variety of simulation purposes to demonstrate code function between a companion computer such as the Nvidia Jetson Nano (as used in this project) and a flight controller on board a drone.

## Installing Mission Planner
Follow the instructions on the [Arudpilot website](https://ardupilot.org/planner/docs/mission-planner-installation.html) on how to install Mission Planner for different operating systems.


## Running SITL

Open Mission Planner and select the SIMULATION tab from the top menu.

![select simulation](./images/missionPlannerSelectSimulation.jpg)

Select the **multirotor** firmware and then choose the **stable** option.

![select multirotor](./images/missionPlannerMultirotor.jpg)

A screen similar to the following should be displayed. From there the PLAN tab to can be used to create a flight plan through waypoints to simulate a basic test flight.

In the top right corner it displays the connection status and the port and baud rate being used. By default Mission Planner uses TCP connection with port 5760. This may need to be changed to either 5762 or 5763 depending on what port the software program uses as it needs to be using a different one to Mission Planner.

When pressing DISCONNECT the port being used and the connection type can be changed and then Mission Planner can reconnect to the simulation by pressing the CONNECT button.

![simulation main page](./images/missionPlannerData.jpg)

To run **GPSInject-GetReults.py** the parameter list must first be altered in Mission Planner. Press the CONFIG tab then click on the Full Parameter List. Search GPS and alter the checked favourited fields as shown in the image below.

  

GPS_AUTO_SWITCH 2

GPS_INJECT_TO 1

GPS_PRIMARY 0

GPS_TYPE 1

GPS_TYPE2 14

SIM_GPS2_DISABLE 0

![parameters](./images/missionPlannerPreferences.jpg)

  
<a id="jetson"></a>
# Jetson Nano 
The Jetson is our companion computer for this project, it communicates to the flight controller using a serial UART connection. Using PyMavlink to send Mavlink commands and receive messages from the flight controller, the Jetson has control over nearly every aspect of the drone, for our purposes though, we'll only be requesting GPS data and sending it.
  
## Installing Jetson Nano OS

You'll need:
 - a SD card reader
 - preferably a Linux computer of sorts (though it can be done with windows too) 
 - a decent 2A minimum usb power supply and type c cable to suit
 - a micro usb type b cable

The Jetson requires an older OS than that of the guide on the Nvidia website as the most current OS version as of August 2022 is corrupt. Follow the guide [here](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-2gb-devkit) to install the operating system to the Jeston 2Gb, be sure to get an older version of the operating system if Nvidia hasnt released a new version since August 2022.


## Connecting to Ardupilot through PyMavlink

### Installing PyMavlink
Note: Running PyMavlink on Jetson Nano will require installing libxml2 and libxslt first
```bash
sudo apt-get install libxml2-dev libxslt-dev python-dev
```
```bash
pip3 install pymavlink
```

The basic tests to check if the Jetson is connected to the drone through PyMavlink are found in [this folder](testFiles). Specifically a good start is [the GPS test](testFiles/gps.py) that gets the GLOBAL_POSITION_INT data from the drone using the serial port and prints it as it goes.
From here one can test if the position data recieved matches, the current GPS co-ordinates of the drone, and that of the controller connected to the drone. 

The serial port may need to be changed if there is no connection, on either the Jetson, or the drone. Changing the drones parameters of the serial port the Jetson is connected to, to "Mavlink", might help if the drones auto setting isn't picking up the commands.
Changing the connection port in the gps.py code in line 6 may also help if you are plugged into the wrong serial port on the Jetson. 
Always check that Tx and Rx are the right way round.
