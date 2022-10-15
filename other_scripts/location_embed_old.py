# Name: location_embed.py
# Author: Alex Jennings 102117465
# Description: Associate GPS coordinates with each satellite image by embedding within it's EXIF data.
# Reads a list of coordinates associated with an image name from a CSV file and embeds.

# Uses 'exif' library for EXIF manipulation. To install, 'pip install exif'.
# import exif
# Uses 'pandas' library for CSV operations. To install, 'pip install pandas'.
import pandas as pd
# Regular I/O and system operations
import os
# Let us get the time (self explanatory!)
import time
# Library to manipulate geospatial information
import geopy
# Basic math functions
import math
# Pillow - Python Image Library
from PIL import Image
from PIL.ExifTags import GPSTAGS
# PathLib - handle file paths properly
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath, WindowsPath
# Tyf - handle EXIF
import Tyf





import sys
import cv2

# Read image file data from CSV, and evaluate if they exist or not within a directory and its subdirectories
def fileEnum(csv_file, root_path):
    # Read the CSV file into a dataframe
    coordCSV = pd.read_csv(
        filepath_or_buffer = csv_file,
        sep = ','
    )
    
    # Extract the filenames column from the CSV and store in an array
    satimg_names = coordCSV['FileNames'].values
    satimg_lat = coordCSV['Latitude'].values
    satimg_lon = coordCSV['Longitude'].values
    satimg_loc = []
    
    for i in range(0, len(satimg_lat)):
        satimg_loc.append({"lat": satimg_lat[i], "lon": satimg_lon[i]})
    
    # Evaluate and store the file/directory structure of the root dir and all subdirs
    dir_structure = os.walk(root_path)
    
    # Init arrays/lists to hold the data we need
    found_fnames = []
    found_fpaths = []
    matched_files = []
    unmatched_files = []
    
    # Iterate over the 3-tuples in the dir_structure list and concat all the filenames and paths into two respective lists
    # There is the same number of files as there is paths to them, and they are sequentially read and appendeded to the array.
    # This ensures that there is a 1-1 correlation between filenames and paths at the same index of each respective array.
    for directory in dir_structure:
        # Iterate over the filename array associated with each directory level
        for name in directory[2]:
            # For each file name in the directory, append its name and its path to the end of the name and path arrays
            found_fnames.append(name)
            comb_path = os.path.join(directory[0], name)
            found_fpaths.append(comb_path)
        
    # Iterate over the filename and path lists in parallel, and sort file names and paths that do/do not match values from the CSV into respective arrays
    
    for iname, iloc in zip(satimg_names, satimg_loc):
        matchedimg = False
        
        for fname, fpath in zip(found_fnames, found_fpaths):
            if fname == iname:
                matchedimg = True
                break
            else:
                continue
        if matchedimg:
            matched_files.append({"filename": fname, "filepath": fpath, "imageloc": iloc})
        else:
            unmatched_files.append({"filename": iname, "imageloc": iloc})

    # Return a dict containing the matched and unmatched file arrays
    dict = {"matched": matched_files, "unmatched": unmatched_files}
    
    print(dict["matched"])
    
    return dict

# Log the results of the embedding operation to a CSV
def logResults(file_dict):
    copy_dict = file_dict
    matched = file_dict["matched"]
    unmatched = file_dict["unmatched"]
    delta_len = len(matched) - len(unmatched)
    for i in range(0, abs(delta_len)):
        if (delta_len == 0):
            continue
        elif (delta_len < 0):
            matched.append("None")
        elif (delta_len > 0):
            unmatched.append("None")
    # update the dictionary with the padded array
    copy_dict["matched"] = matched
    copy_dict["unmatched"] = unmatched
    # Dynamically generate logfile name from the current time
    logtime = time.localtime()
    logfile_name = "embed_log" + str(logtime.tm_year) + "_" + str(logtime.tm_mon) + "_" + str(logtime.tm_mday) + "_" + str(logtime.tm_hour) + str(logtime.tm_min) + str(logtime.tm_sec) + ".txt"
    print("Logfile name is: " + logfile_name)
    # Turn the dictionary into a pandas dataframe
    log_df = pd.DataFrame.from_dict(data = copy_dict, orient = 'columns')
    # Save the pandas dataframe in CSV format
    log_df.to_csv("./" + logfile_name)

# Convert coordinates both to and from DMS and decimal degrees.
#
# Args:
#   input: the coordinates to convert in DMS as a 4-entry dictionary, or decimal degrees as a signed float
#   type: selection string - "lat", "lon" - are we working with latitude or longitude
#   conversion: selection string - "dec", "dms" - convert to decimal from DMS or vice-versa
#
# Return Data Types:
#   converting from decimal deg to DMS - return value is a 4-entry dictionary
#   converting from DMS to decimal deg - return value is a signed float
def locConverter(input, type, conversion):
    match type:
        # If we are converting latitude
        case "lat":
            match conversion:
                # If we are converting to DMS from signed decimal degrees
                case "dms":
                    if input < 0:
                        loc_dir = "W"
                    elif input > 0:
                        loc_dir = "E"
                    else:
                        loc_dir = "NA"
                    input = abs(input)
                    loc_deg = math.floor(input)
                    input = (input - loc_deg)*60
                    loc_min = math.floor(input)
                    input = (input - loc_min)*60
                    loc_sec = input
                    return {"degrees": loc_deg, "minutes": loc_min, "seconds": loc_sec, "direction": loc_dir}
                # If we are converting to signed decimal degrees from DMS
                case "dec":
                    if input["direction"] == "E":
                        mult = -1
                    else:
                        mult = 1
                    loc_dec_deg = input["degrees"]
                    loc_dec_min = input["minutes"] / 60
                    loc_dec_sec = input["seconds"] / 360
                    return (mult*(loc_dec_deg + loc_dec_min + loc_dec_sec))
                case _:
                    raise Exception
        # If we are converting longitude
        case "lon":
            match conversion:
                # If we are converting to DMS from signed decimal degrees
                case "dms":
                    if input < 0:
                        loc_dir = "S"
                    elif input > 0:
                        loc_dir = "N"
                    else:
                        loc_dir = "NA"
                    input = abs(input)
                    loc_deg = math.floor(input)
                    input = (input - loc_deg)*60
                    loc_min = math.floor(input)
                    input = (input - loc_min)*60
                    loc_sec = input
                    return {"degrees": loc_deg, "minutes": loc_min, "seconds": loc_sec, "direction": loc_dir}
                # If we are converting to signed decimal degrees from DMS
                case "dec":
                    if input["direction"] == "S":
                        mult = -1
                    elif (input["direction"] == "N") or (input["direction"] == "NA"):
                        mult = 1
                    loc_dec_deg = input["degrees"]
                    loc_dec_min = input["minutes"] / 60
                    loc_dec_sec = input["seconds"] / 360
                    return (mult*(loc_dec_deg + loc_dec_min + loc_dec_sec))
                case _:
                    raise Exception
        case _:
            raise Exception
                
# Update the location data returned as part of file enumeration so that it is in the appropriate format for EXIF fields.
# Args: list of file data that is to be updated
def locUpdater(file_list):
    # for each file in the list
    for file in file_list:
        # Read the lat and lon values in decimal degrees
        latitude_dec = file["imageloc"]["lat"]
        longitude_dec = file["imageloc"]["lon"]
        # Convert the values from decimal degrees to dms
        latitude_dms = locConverter(latitude_dec, "lat", "dms")
        longitude_dms = locConverter(longitude_dec, "lon", "dms")
        # Update the lat and lon for the particular file with the converted DMS values
        file["imageloc"]["lat"] = latitude_dms
        file["imageloc"]["lon"] = longitude_dms   

# Add location data to the matched files as EXIF fields
# def exifWriteOld(fmatched):
#     # Init the image array. Stores binary image data read from file.
#     imageArr = []
#     # Iterate over the matched image array, opening an image and appending to the image array upon each iteration.
#     for img_data in fmatched:
#         with open(img_data["filepath"], "rb") as img_file:
#             current_img = exif.Image(img_file)
#             imageArr.append(current_img)
#     # Iterate in parallel over the image array and the matched image array, fetching and setting EXIF field values for each respective image.       
#     for image, img_data in zip(imageArr, fmatched):
#         tag_data = img_data["imageloc"]
#         image.set("gps_latitude", (tag_data["lat"]["degrees"], tag_data["lat"]["minutes"], tag_data["lat"]["seconds"]))
#         image.set("gps_latitude_ref", tag_data["lat"]["direction"])
#         image.set("gps_longitude", (tag_data["lon"]["degrees"], tag_data["lon"]["minutes"], tag_data["lon"]["seconds"]))
#         image.set("gps_longitude_ref", tag_data["lon"]["direction"])
#         # Print the recently set attributes to stdout for verification
#         print("Image " + img_data["filename"] + " attributes set:")
#         raw_lat = image.get("gps_latitude")
#         raw_lat_ref = image.get("gps_latitude_ref")
#         raw_lon = image.get("gps_longitude")
#         raw_lon_ref = image.get("gps_longitude_ref")
#         str_lat = str(raw_lat[0]) + " " + str(raw_lat[1]) + " " + str(raw_lat[2]) + " " + raw_lat_ref + "\n"
#         str_lon = str(raw_lon[0]) +  " " + str(raw_lon[1]) + " " + str(raw_lon[2]) + " " + raw_lon_ref + "\n"
#         print("Lat: " + str_lat)
#         print("Lon: " + str_lon)
#     # Iterate over the image and matched image arrays in parallel, writing the modified image files to disk
#     counter = 1
#     for image in imageArr:
#         with open('new_file' + str(counter) + ".jpg", 'wb') as write_img:
#             write_img.write(image.get_file())
#             counter = counter + 1
            
def exifWrite(matched_images):
    # Init the image array. Stores binary image data read from file.
    
    # imageArr = []
    # exifArr = []
    # valueArr = []
    
    # EXIF GPS Tags that we want to edit
    gps_tags = [
        "GPSLatitudeRef",   # GPS Latitude Cardinal Dir
        "GPSLatitude",      # GPS Latitude Values DMS
        "GPSLongitudeRef",  # GPS Longitude Cardinal Dir
        "GPSLongitude"      # GPS Longitude Values DMS
    ]
    # Iterate over the matched image array.
    for img_data in matched_images:
        lat_tags = img_data["imageloc"]["lat"]
        lon_tags = img_data["imageloc"]["lon"]
        # Open an image, fetch the pixel and exif data and append them to their respective arrays.
        
        print(img_data["filepath"])
        current_image = Tyf.open(img_data["filepath"])
                    
        # valueVar = {
        #     "GPSLatitudeRef": lat_tags["direction"],
        #     "GPSLatitude"   : (
        #         float(lat_tags["degrees"]),
        #         float(lat_tags["minutes"]),
        #         float(lat_tags["seconds"])
        #     ),
        #     "GPSLongitudeRef": lon_tags["direction"],
        #     "GPSLongitude"   : (
        #         float(lon_tags["degrees"]),
        #         float(lon_tags["minutes"]),
        #         float(lon_tags["seconds"])
        #     )
        # }
        
        print(lon_tags)
        print(lat_tags)
        print(current_image.ifd0)
                
        current_image.ifd0.set_location(float(lon_tags), float(lat_tags), 0.0)
        current_image.ifd0.set_location(float(lon_tags), float(lat_tags), 0.0)
        current_image.ifd0.set_location(float(lon_tags), float(lat_tags), 0.0)
        current_image.ifd0.set_location(float(lon_tags), float(lat_tags), 0.0)
        
        for i in gps_tags:
            print(current_image[i])
        
        #for exif_tags in current_image.ifd0.tags(): print(exif_tags)
        
        #current_image.ifd0.get_location()
        
        #Tyf.ifd.dump_mapbox_location(current_image.ifd0, "test_output.jpeg")
        
        
        
        # for gpstag in gps_tags:
        #     print("GPS Tag: " + gpstag + "\n") # output the gps tag that we are updating
        #     # for i in range(0, len(GPSTAGS)):
        #     #     if gpstag == GPSTAGS[i]:
        #     #         tag_index = int(i)
            
        #     current_image.ifd0[gpstag] = valueVar[gpstag]
        #     print(type(current_image[gpstag]))
        #     # Check if the exif tag contents is an instance of a tuple
        #     if isinstance(current_image[gpstag], tuple):
        #         print(current_image[gpstag])
        #         print("Tag value updated to:\n" +
        #             "Deg: " + str(current_image[gpstag][0]) + "\n" +
        #             "Min: " + str(current_image[gpstag][1]) + "\n" +
        #             "Sec: " + str(current_image[gpstag][2]) + "\n"
        #         )
        #     else:
        #         print("Tag value updated to: " + str(current_image[gpstag]) + "\n") # output the newly changed value of the tag
        
        # Save the updated image to file.
        print(img_data["filepath"])
        current_image.save(str(img_data["filepath"]))
                    
            
            
        
        # with Image.open(img_data["filepath"]) as image:
        #     exif = image.getexif()
        #     imageArr.append(
        #         {
        #             "image": image,
        #             "path" : img_data["filepath"]
        #         })
        #     exifArr.append(exif)
        #     print(exif)
        #     image.close()
        
        
        # Make an array of GPS tags for the current image.
        # Tags stored in a dict with same names as the tags to which they will be equated. Lets us use less variables in the iterator.
        # Lat and lon values are 3 floats, they are stored in the dict as a 3-tuple.
        # valueArr.append(
            # {
            #     "GPSVersionID"  : '2 0 0 0',
            #     "GPSLatitudeRef": lat_tags["direction"],
            #     "GPSLatitude"   : (
            #         float(lat_tags["degrees"]),
            #         float(lat_tags["minutes"]),
            #         float(lat_tags["seconds"])
            #     ),
            #     "GPSLongitudeRef": lon_tags["direction"],
            #     "GPSLongitude"   : (
            #         float(lon_tags["degrees"]),
            #         float(lon_tags["minutes"]),
            #         float(lon_tags["seconds"])
            #     )
            # }
            # )
        
    # for img_instance, exif_instance, value_instance in zip(imageArr, exifArr, valueArr):
    #     # Update the gps tag values with the new location values
    #     for gpstag in gps_tags:
    #         print("GPS Tag: " + gpstag + "\n") # output the gps tag that we are updating
    #         for i in range(0, len(GPSTAGS)):
    #             if gpstag == GPSTAGS[i]:
    #                 tag_index = int(i)
            
    #         exif_instance[tag_index] = value_instance[gpstag]
    #         print(type(exif_instance[tag_index]))
    #         # Check if the exif tag contents is an instance of a tuple
    #         if isinstance(exif_instance[tag_index], tuple):
    #             print(exif_instance[tag_index])
    #             print("Tag value updated to:\n" +
    #                   "Deg: " + str(exif_instance[tag_index][0]) + "\n" +
    #                   "Min: " + str(exif_instance[tag_index][1]) + "\n" +
    #                   "Sec: " + str(exif_instance[tag_index][2]) + "\n"
    #             )
    #         else:
    #             print("Tag value updated to: " + str(exif_instance[tag_index]) + "\n") # output the newly changed value of the tag
                
        # # Write the image data to file at the same path as it was read from, with the new EXIF data
        # loaded_image = img_instance["image"]
        # print(loaded_image) # test to verify that we have the image loaded
        # output_path = img_instance["path"].replace(os.altsep, os.sep)
        # print(output_path) # test to verify that the output path is loaded
        # print(exif_instance)
        # with Image.open(output_path) as saveImage:
        #     saveImage.save(fp = output_path, exif = exif_instance)
        #     saveImage.close()

# main function that runs everything we need.
def main():
    # Enumerate images, their paths, and their associated coordinates
    image_dict = fileEnum("sample_imagecoords.csv", ".\\test_embed_images")
    # Log the results of the matching operation to file
    #logResults(image_dict)
    # Get the found files from the dictionary
    matched_list = image_dict["matched"]
    # Update the location coordinates in the list to be DMS instead of decimal degrees
    # locUpdater(matched_list)
    # Write the new coordinates to the image files
    exifWrite(matched_list)

##### Code to be run #####
main()