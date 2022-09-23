
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

#start mavlink connection and wait for heartbeat, then print heartbeat on success
#prevents connection failures and ensures secure connection
the_connection = mavutil.mavlink_connection(connString)
print("Heartbeat from system (system %u component %u)" % (the_connection.target_system, the_connection.target_component))


#main loop to inject the GPS coordinates

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
    GPSInject(the_connection, injection)
    
    #print results if they are working
    GPSGetResults(injection,getRawGPS1,getcurrentGlobal)
    #store data to a CSV file
    CSVDataStorage(getcurrentGlobal,getRawGPS1,injection)


