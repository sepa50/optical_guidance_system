## authors: Tyler Smith 100039114, Jonothan Ridgeway 102119636, Alex Jennings 102117465
## gps code injector, with CSV output

from pymavlink import mavutil
import time
import CSVDataStorage as csv

#if windows doesnt let you run the script properly due to permission errors, enter the following in the terminal
# Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned


###TODO auto connection attempt
# portOptions = ["5760", "5762", "5763"]

# # attempt a connection

# for i in range(3):
#     connStringComb = connString + portOptions[i]
#     the_connection = mavutil.mavlink_connection(connStringComb)
#     connHB = the_connection.recv_match(type='HEARTBEAT', blocking=False, timeout=None)
#     if connHB is not None:
#         break
#     else:
#         the_connection.close()
#         continue

#data to inject
injection = {'lat':-35.3599712, 'lon':149.1542315}

##connection string ( change port to 5762,5760, 5763 as needed, missionplanner is fussy)
connString = "tcp:127.0.0.1:5760"

the_connection = mavutil.mavlink_connection(connString)
print("Heartbeat from system (system %u component %u)" % (the_connection.target_system, the_connection.target_component))


#result printer to show the data in terminal
def printResults(injection ,getRawGPS1, getcurrentGlobal): 
    
    #get global positional data
    globalLat = getcurrentGlobal.lat*10**(-7)
    globalLong = getcurrentGlobal.lon*10**(-7)
   
    #get raw gps1 data
    rawLat = getRawGPS1.lat*10**(-7)
    rawLon = getRawGPS1.lon*10**(-7)
    
    #find error in injected data
    injectErrorLat = round((rawLat - injection["lat"]),7)
    injectErrorLon = round((rawLon - injection["lon"]),7)

    #print results
    printbar = "\n=============================================\n"
    
    globalResult = "Global co ordinate = " + str(round(globalLat,7)) +", " + str(round(globalLong,7))
    injectResult = "injected co ordinates = " + str(injection["lat"]) +", " + str(injection["lat"])
    injectError = "Error in tracking = " + str(injectErrorLat) + ", " + str(injectErrorLon)
    rawResult = "Raw co ordinates from GPS actual = " + str(rawLat) + ", " +str(rawLon)
    print(printbar + injectError + printbar + globalResult + printbar + injectResult + printbar + rawResult)
    

def injectGPS(injectLat, InjectLon):
    ### this is where the magic happens, GPS injection, the only required lines are the lat and lon, then the sattelite count
    #TODO adjust sattelite count according to what gives reasonable accuracy.
    the_connection.mav.gps_input_send(
        0,  # Timestamp (micros since boot or Unix epoch)
        2,  # ID of the GPS for multiple GPS inputs
        # Flags indicating which fields to ignore (see GPS_INPUT_IGNORE_FLAGS enum).
        # All other fields must be provided.
        (mavutil.mavlink.GPS_INPUT_IGNORE_FLAG_VEL_HORIZ |
         mavutil.mavlink.GPS_INPUT_IGNORE_FLAG_VEL_VERT |
         mavutil.mavlink.GPS_INPUT_IGNORE_FLAG_SPEED_ACCURACY),
        0,  # GPS time (milliseconds from start of GPS week)
        0,  # GPS week number
        3,  # 0-1: no fix, 2: 2D fix, 3: 3D fix. 4: 3D with DGPS. 5: 3D with RTK
        int(injectLat*10**(-7)),  # Latitude (WGS84), in degrees * 1E7
        int(injectLon*10**(-7)),  # Longitude (WGS84), in degrees * 1E7
        10,  # Altitude (AMSL, not WGS84), in m (positive for up)
        1,  # GPS HDOP horizontal dilution of position in m
        1,  # GPS VDOP vertical dilution of position in m
        0,  # GPS velocity in m/s in NORTH direction in earth-fixed NED frame
        0,  # GPS velocity in m/s in EAST direction in earth-fixed NED frame
        0,  # GPS velocity in m/s in DOWN direction in earth-fixed NED frame
        0,  # GPS speed accuracy in m/s
        1,  # GPS horizontal accuracy in m
        1,  # GPS vertical accuracy in m
        9   # Number of satellites visible.
    )

#create CSV file for data logging
def createCSV(getcurrentGlobal,getRawGPS1,injection):
    csv.csvCreate(getcurrentGlobal,getRawGPS1,injection)


#main loop to inject the GPS coordinates
while True:
    ### fake co ords to inject
    #TODO change these to user inputs from the model
    injectLat = -35.3599712
    injectLon = 149.1542315
    #time span between pushes
    time.sleep(1)    
    getcurrentGlobal = the_connection.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    getRawGPS1 = the_connection.recv_match(type='GPS_RAW_INT', blocking=True)

    #do the inject
    injectGPS(injection["lat"], injectLon["lon"])

    #print results if they are working
    printResults(injection,getRawGPS1,getcurrentGlobal)
    csv.csvCreate(getcurrentGlobal,getRawGPS1,injection)