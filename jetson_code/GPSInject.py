## Authors: Tyler Smith 100039114, Jonothan Ridgeway 102119636
# inject GPS data using a dict structure of injection= {"lat": val, "lon": val, "confidence":6-25}
# confidence sets the satelite count to apply a level of "accuracy" given lack of accuracy setting

import pymavlink
from pymavlink import mavutil


def injectGPS(connection, injection):
    ### this is where the magic happens, GPS injection, the only required lines are the lat and lon, then the sattelite count
    #TODO adjust sattelite count according to what gives reasonable accuracy.
    connection.mav.gps_input_send(
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
        int(injection["lat"]*10**(7)),  # Latitude (WGS84), in degrees * 1E7
        int(injection["lon"]*10**(7)),  # Longitude (WGS84), in degrees * 1E7
        10,  # Altitude (AMSL, not WGS84), in m (positive for up)
        1,  # GPS HDOP horizontal dilution of position in m
        1,  # GPS VDOP vertical dilution of position in m
        0,  # GPS velocity in m/s in NORTH direction in earth-fixed NED frame
        0,  # GPS velocity in m/s in EAST direction in earth-fixed NED frame
        0,  # GPS velocity in m/s in DOWN direction in earth-fixed NED frame
        0,  # GPS speed accuracy in m/s
        1,  # GPS horizontal accuracy in m
        1,  # GPS vertical accuracy in m
        injection["confidence"]   # Number of satellites visible. determines the accuracy. between 6 and ?25
    )
