## authors: Tyler Smith 100039114, Alex Jennings 102117465
#creates a csv file to store the gathered data

import pandas as pd
import os
from datetime import datetime

#create a CSV file using the variables gathered from teh GPS Inject script
def csvCreate(globalInt, rawInt, injection):
    currentTime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    data = {
        "Timestamp":[currentTime],
        "Global_Int_Lat":[round(globalInt.lat*10**(-7),7)],
        "Global_Int_Lon":[round(globalInt.lon*10**(-7),7)],
        "Raw_GPS_Lat":[round(rawInt.lat*10**(-7),7)],
        "Raw_GPS_Lon":[round(rawInt.lon*10**(-7),7)],
        "Injected_Lat":[injection["lat"]],
        "Injected_Lon":[injection["lon"]]

        #TODO add error to csv ouput ALEX 
    }


    df = pd.DataFrame(data)
    print(df)
    #TODO iterative naming convention for the file type.
    output_path='my_csv.csv'
    df.to_csv(output_path,index=False, mode='a', header=not os.path.exists(output_path))