### Authors: Tyler Smith 100039114, Jonothan Ridgeway 102119636, Alex Jennings 102117465
### main loop for the jetson

import pymavlink, CSVDataStorage, GPSGetResults, GPSInject, CamSettings
import time
import cv2
from pymavlink import mavutil
from datetime import datetime

### fake co ords to inject
#TODO change these to user inputs from the model
###latitude, longitude and level of confidence in terms of sattelites
injection = {'lat':-35.3599712, 'lon':149.1542315, "confidence":20}

### Attempt a tcp connection auto loop for each potential port uncomment if needed 

#connString = "tcp:127.0.0.1:"
#portOptions = ["5760", "5762", "5763"]
#for port in portOptions:
#	connStringComb = connString + port
#	the_connection = mavutil.mavlink_connection(connStringComb)
#	connHB = the_connection.wait_heartbeat()
#	if connHB is not None:
#		print("Heartbeat from system (system %u component %u)" % (the_connection.target_system, the_connection.target_component))
#		break
#	else:
#		the_connection.close()
#		continue

### Serial connection to drone. comment if using tcp
the_connection = mavutil.mavlink_connection("/dev/ttyTHS1", 115200)

### Start mavlink connection and wait for heartbeat, then print heartbeat on success
### Prevents connection failures and ensures secure connection
print("Heartbeat from system (system %u component %u)" % (the_connection.target_system, the_connection.target_component))

### Message requester, sets interval for drone to push messages to the Jetson. 
### requires a Mavlink message string to set the message to request and float frequency in hertz to set the push rate.

def request_message_interval(message_input, frequency_hz):

	message_name = "MAVLINK_MSG_ID_" + message_input
	message_id = getattr(mavutil.mavlink, message_name)
	### send message
	the_connection.mav.command_long_send(
		the_connection.target_system, the_connection.target_component,
		mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
		message_id,
		1e6 / frequency_hz,
		0,
		0, 0, 0, 0)
	### print on send
	print("Requested the message successfully.")

### Request require messages at a 10hz rate
request_message_interval("GLOBAL_POSITION_INT",10.0)
request_message_interval("GPS_RAW_INT",10.0)

### Start camera stream
print(CamSettings.gstreamer_pipeline(flip_method=0))
video_capture = cv2.VideoCapture(CamSettings.gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)

### Main loop to inject the GPS coordinates, store the current GPS co ordinates of both raw onboard and injected
### also does the Camera function calling to take and store images. 
if video_capture.isOpened():
	try:

		###camera loop end if you want limited photos uncomment below lines
		i = 0		
		while True:
		    ### get current time for timestamping csv and images respectively
			currentTime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
			ptime = datetime.now().strftime("%H%M%S")

			### capture camera image and save it with the timestamp
			ret_val, frame = video_capture.read()
			cv2.imwrite("output/"+str(ptime)+".png", frame)
			
			###get GPS data for manipulation, used for CSVData storage
			getcurrentGlobal = the_connection.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
			getRawGPS1 = the_connection.recv_match(type='GPS_RAW_INT', blocking=True)
			
			### do the inject
			#GPSInject.injectGPS(the_connection, injection)
			
			### print results
			GPSGetResults.printResults(injection,getRawGPS1,getcurrentGlobal)
    		### store data to a CSV file
			CSVDataStorage.csvCreate(getcurrentGlobal,getRawGPS1,injection,currentTime)
			
			###camera loop end if you want limited photos uncomment below lines
			#i+=1
			
			time.sleep(1)
			###camera loop end if you want limited photos, set limit here
			if i >= 100:
				break

	finally:
		#release pipepline on finish or ctrl+c
		video_capture.release()

else:
	#failed to load camera
	print("Error: Unable to open camera")
