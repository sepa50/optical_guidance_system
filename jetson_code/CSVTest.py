from ast import Index
import pandas as pd
import os


data = {
  "Global_Int_Lat":[140],
  "Global_Int_Lon":[140],
  "Injected_Lat":[120],
  "Injected_Lon":[121],
  "Raw_GPS_Lat":[130],
  "Raw_GPS_Lon":[131]
}
df = pd.DataFrame(data, index=["timestamp numbers woo"])
print(df)
output_path='my_csv.csv'
df.to_csv(output_path, mode='a', header=not os.path.exists(output_path))