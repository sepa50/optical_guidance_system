## Authors: Tyler Smith 100039114, Alex Jennings 102117465
# Creates a csv file to store the gathered data

import pandas as pd
import os

import geopy.distance

#create a CSV file using the variables gathered from teh GPS Inject script
def csvCreate(globalInt, rawInt, injection, timestamp):
	currentTime = timestamp
    diff_err_lat = rawInt.lat*10**(-7) - injection["lat"]
    diff_err_lon = rawInt.lon*10**(-7) - injection["lon"]
    inj_latlon = (injection["lat"], injection["lon"])
    raw_latlon = (rawInt.lat*10**(-7), rawInt.lon*10**(-7))
    distance_err = geopy.distance.geodesic(inj_latlon, raw_latlon).m
    
    data = {
        "Timestamp":[currentTime],
        "Global_Int_Lat":[round(globalInt.lat*10**(-7),7)],
        "Global_Int_Lon":[round(globalInt.lon*10**(-7),7)],
        "Raw_GPS_Lat":[round(rawInt.lat*10**(-7),7)],
        "Raw_GPS_Lon":[round(rawInt.lon*10**(-7),7)],
        "Injected_Lat":[injection["lat"]],
        "Injected_Lon":[injection["lon"]],
        "Diff_Err_Lat":[diff_err_lat],
        "Diff_Err_Lon":[diff_err_lon],
        "Distance_Error":[distance_err]
    }

    df = pd.DataFrame(data)
    #print(df)
    #TODO iterative naming convention for the file type.
    output_path='my_csv.csv'
    df.to_csv(output_path,index=False, mode='a', header=not os.path.exists(output_path))
