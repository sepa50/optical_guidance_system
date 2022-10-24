# Contents
 - [SITL install](#sitlInstall)
	 - [Installing Mission planner](#installMP)
	 - [Running SITL](#runSITL)
 - [Jetson Nano setup](#jetson)
	 - [Installing Jetson Nano OS](#JetsonOS)
	 - [Connecting to Ardupilot through PyMavlink](#PymavlinkArdu)
 - [Camera set up](#cameraSetup)
 - [Jetson Loop](#jetsonloop)
	 - [What each script does](#whatscript)
	 - [What the loop does](#whatloop)

# SITL Simulation on desktop <a id="sitlInstall"></a>
Software in the Loop (SITL) can be used to simulate Ardupilot. it can be used for a variety of simulation purposes to demonstrate code function between a companion computer such as the Nvidia Jetson Nano (as used in this project) and a flight controller on board a drone.
## Installing Mission Planner <a id="installMP"></a>
Follow the instructions on the [Arudpilot website](https://ardupilot.org/planner/docs/mission-planner-installation.html) on how to install Mission Planner for different operating systems.

## Running SITL <a id="runSITL"></a>
 

Open Mission Planner and select the SIMULATION tab from the top menu.

![select simulation](./images/missionPlannerSelectSimulation.jpg)

Select the **multirotor** firmware and then choose the **stable** option.

![select multirotor](./images/missionPlannerMultirotor.jpg)

A screen similar to the following should be displayed. From there the PLAN tab to can be used to create a flight plan through waypoints to simulate a basic test flight.

In the top right corner it displays the connection status and the port and baud rate being used. By default Mission Planner uses TCP connection with port 5760. This may need to be changed to either 5762 or 5763 depending on what port the software program uses as it needs to be using a different one to Mission Planner.

When pressing DISCONNECT the port being used and the connection type can be changed and then Mission Planner can reconnect to the simulation by pressing the CONNECT button.

![simulation main page](./images/missionPlannerData.jpg)

To run **GPSInject-GetReults.py** the parameter list must first be altered in Mission Planner. Press the CONFIG tab then click on the Full Parameter List. Search GPS and alter the checked favourited fields as shown in the image below.

```bash
GPS_AUTO_SWITCH 2

GPS_INJECT_TO 1

GPS_PRIMARY 0

GPS_TYPE 1

GPS_TYPE2 14

SIM_GPS2_DISABLE 0
```
  

![parameters](./images/missionPlannerPreferences.jpg)

  

# Jetson Nano <a id="jetson"></a>
The Jetson is our companion computer for this project, it communicates to the flight controller using a serial UART connection. Using PyMavlink to send Mavlink commands and receive messages from the flight controller, the Jetson has control over nearly every aspect of the drone, for our purposes though, we'll only be requesting GPS data and sending it.
 
## Installing Jetson Nano OS <a id="JetsonOS"></a>

You'll need:
 - a SD card reader
 - preferably a Linux computer of sorts (though it can be done with windows too) 
 - a decent 2A minimum usb power supply and type c cable to suit
 - a micro usb type b cable

The Jetson requires an older OS than that of the guide on the Nvidia website as the most current OS version as of August 2022 is corrupt. Follow the guide [here](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-2gb-devkit) to install the operating system to the Jeston 2Gb, be sure to get an older version of the operating system if Nvidia hasnt released a new version since August 2022.

## Connecting to Ardupilot through PyMavlink <a id="PymavlinkArdu"></a>

### Installing PyMavlink
Note: Running PyMavlink on Jetson Nano will require installing libxml2 and libxslt first
```bash
sudo apt-get install libxml2-dev libxslt-dev python-dev
```
```bash
pip3 install pymavlink
```
### Testing the Connection
The basic tests to check if the Jetson is connected to the drone through PyMavlink among various other useful tests are found in [this folder](testFiles). Specifically a good start is [the GPS test](testFiles/gps.py) that gets the GLOBAL_POSITION_INT data from the drone using the serial port and prints it as it goes.
From here one can test if the position data recieved matches, the current GPS co-ordinates of the drone, and that of the controller connected to the drone. 

The serial port may need to be changed if there is no connection, on either the Jetson, or the drone. Changing the drones parameters of the serial port the Jetson is connected to, to "Mavlink", might help if the drones auto setting isn't picking up the commands.
Changing the connection port in the gps.py code in line 6 may also help if you are plugged into the wrong serial port on the Jetson. 
Always check that Tx and Rx are the right way round.

# Camera Setup <a id="cameraSetup"></a>
lol what do we write for this?


## Taking photos
- test doc
- explain loop quick


# Jetson Loop <a id="jetsonloop"></a>


## What each script does <a id="whatscript"></a>
### - [GPSGetResults](GPSGetResults.py)
This script is mainly for test purposes and mainly just receives all the dictionaries of all the different parameters and prints them to console in a legible format for verification that the code runs smoothly, the line running this script in the loop can be commented out so as to increase optimization and runtime.

### - [GPSInject](GPSInject.py)
Injects the input GPS co-ordinates to the drone using the gps_input_send() method from PyMavlink. The important things to note is that it takes in a connection ( ArduPilot connection ) and a injection dictionary following the format of :
```python
injection = {'lat': 0.0, 'lon' 0.0, 'confidence' = 0}
```
Where Lat and lon are Latitude and Longitude respectively and confidence is the level of confidence of which the model has provided as to where the drone is currently.
The level of confidence is a value from 0-20 to represent the number of "GPS satellites" the drone can see. In practice this is really just a number to provide a rough mapping to a percentage of confidence the model provides on each co-ordinate push so that the drone can account for errors and modify it based on other data available such as optical flow and inertial referencing.

### - [CSVDataStorage](CSVDataStorage.py)
CSV data storage stores the data from the flight as a CSV file for further manipulation to verify the systems accuracy. CSV data storage takes in the dictionaries of the GLOBAL_POSITION_INT, RAW_GPS, injection data and the current time. If there is no csv made yet matching the scripts file name, it will create one, if there is, it will append it with the new data.
Once a flight is complete, one can graph the relative error between actual GPS Co-ordinates and Model Co-ordinates to see how accurate the Model is. 

### - [CamSettings](CamSettings.py)
This file simply holds the settings for the camera to function as it currently does, main changes that can and may need to be adjusted depending on environment are the wbmode and the aelock.
aelock can be set to 0 or 1, to change the auto exposure lock on the camera to prevent flickering in dark environments or extremely bright environments.

wbmode changes the white balance color correction of the camera depending on environment, this is 0-9 
```bash
- wbMode" Default: 1, "auto"
    - (0): off
    - (1): auto
    - (2): incandescent
    - (3): fluorescent
    - (4): warm-fluorescent
    - (5): daylight
    - (6): cloudy-daylight
    - (7): twilight
    - (8): shade
    - (9): manual
```

## What the loop does <a id="whatloop"></a>
The main point of the loop is to provide a continuous loop to run each script as required. The loop initiallizes a few key components as it starts, as noted in the comments for the loop.
The loop starts by setting up the connection to the drone or simulator, either by serial or a tcp connection. Comment out the section for serial if needed or the tcp section as noted, do not attempt to use both.
After conneciton, the code will hold on no connection, and attempt to request messages to be sent at a 10hz update rate this can be increased if required. From here, the loop will set up the camera, and begin the actual loop. 
The main loop process will:
- Take a photo
- Get Global and GPS co-ordinates
- Inject Co-ordinates
- Print the data if needed
- Add the data to the CSV
- Increment the the loop if a limited loop is set
- sleep for 1 second
- check the loop break and restart

On exit of the loop, the camera will capture release to free up the Gstreamer pipeline.
