from pickletools import long1
import pandas as pd
import os
from datetime import datetime

def csvCreate(globalInt, rawInt, injectLat, injectLon):
    currentTime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    data = {
        "Timestamp":[currentTime],
        "Global_Int_Lat":[round(globalInt.lat*10**(-7),7)],
        "Global_Int_Lon":[round(globalInt.lon*10**(-7),7)],
        "Raw_GPS_Lat":[round(rawInt.lat*10**(-7),7)],
        "Raw_GPS_Lon":[round(rawInt.lon*10**(-7),7)],
        "Injected_Lat":[injectLat],
        "Injected_Lon":[injectLon]
    }


    df = pd.DataFrame(data)
    print(df)
    output_path='my_csv.csv'
    df.to_csv(output_path,index=False, mode='a', header=not os.path.exists(output_path))