### Authors: Tyler Smith 100039114, Alex Jennings 102117465
### Creates a csv file to store the gathered data, requires the global_position_int, raw_gps, injection and a timestamp
### will push each variable in terms of lat and lon, then calculate the error based on this in meters for accuracy.
### creates a csv if one is not available matching the name, and appends if there is one matching the name.

import pandas as pd
import os
import geopy.distance

### Create a CSV file using the variables gathered from teh GPS Inject script
def csvCreate(globalInt, rawInt, injection, timestamp):
	currentTime = timestamp
	diff_err_lat = rawInt.lat*10**(-7) - injection["lat"]
	diff_err_lon = rawInt.lon*10**(-7) - injection["lon"]
	inj_latlon = (injection["lat"], injection["lon"])
	raw_latlon = (rawInt.lat*10**(-7), rawInt.lon*10**(-7))
	distance_err = geopy.distance.geodesic(inj_latlon, raw_latlon).m
    ### put data into a dictionary for pushing to csv
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
	### add data to pandas data frame
	df = pd.DataFrame(data)
	output_path='launchday.csv'
	### push data to csv
	df.to_csv(output_path,index=False, mode='a', header=not os.path.exists(output_path))
