## Authors: Tyler Smith 100039114, Jonothan Ridgeway 102119636
# main loop for the jetson


import pymavlink, CSVDataStorage, GPSGetResults, GPSInject
import time
from pymavlink import mavutil


### fake co ords to inject
#TODO change these to user inputs from the model
#latitude, longitude and level of confidence in terms of sattelites
injection = {'lat':-35.3599712, 'lon':149.1542315, "confidence":20}

#conneciton string for mission planner connection
#TODO add serial connection string
connString = "tcp:127.0.0.1:5760"

### auto connection attempt

connString = "tcp:127.0.0.1:"
portOptions = ["5760", "5762", "5763"]

# attempt a connection

for port in portOptions:
    connStringComb = connString + port
    the_connection = mavutil.mavlink_connection(connStringComb)
    connHB = the_connection.wait_heartbeat()
    if connHB is not None:
        print("Heartbeat from system (system %u component %u)" % (the_connection.target_system, the_connection.target_component))
        break
    else:
        the_connection.close()
        continue

#start mavlink connection and wait for heartbeat, then print heartbeat on success
#prevents connection failures and ensures secure connection
#the_connection = mavutil.mavlink_connection(connString)
#print("Heartbeat from system (system %u component %u)" % (the_connection.target_system, the_connection.target_component))
# main loop to inject the GPS coordinates, store the current GPS co ordinates of both raw onboard and injected
# also does the Camera function calling to take and store images. 

#TODO look if we should be heartbeating during main loop
while True:
    #time delay for each loop
    time.sleep(1)

    #get GPS data for manipulation, used for CSVData storage
    getcurrentGlobal = the_connection.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    getRawGPS1 = the_connection.recv_match(type='GPS_RAW_INT', blocking=True)

    
    # and this is where the image taking and processing would be IF WE HAD A CAMERA!

    #do the inject
    #comment if needed
    GPSInject.injectGPS(the_connection, injection)
    
    #print results if they are working
    GPSGetResults.printResults(injection,getRawGPS1,getcurrentGlobal)
    #store data to a CSV file
    #CSVDataStorage.csvCreate(getcurrentGlobal,getRawGPS1,injection)


