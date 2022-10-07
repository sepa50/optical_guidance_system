# Name: location_embed.py
# Author: Alex Jennings 102117465
# Description: Associate GPS coordinates with each satellite image by embedding within it's EXIF data.
# Reads a list of coordinates associated with an image name from a CSV file and embeds.

# Uses 'exif' library for EXIF manipulation. To install, 'pip install exif'.
import exif
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
    
    for i in satimg_lat:
        satimg_loc.append({"lat": satimg_lat, "lon": satimg_lon})
    
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
            else:
                continue
        if matchedimg:
            matched_files.append({"filename": fname, "filepath": fpath, "imageloc": iloc})
        else:
            unmatched_files.append({"filename": iname, "imageloc": iloc})

    # Return a dict containing the matched and unmatched file arrays
    dict = {"matched": matched_files, "unmatched": unmatched_files}
    return dict

# Log the results of the embedding operation to a CSV
def logResults(file_dict):
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
    file_dict["matched"] = matched
    file_dict["unmatched"] = unmatched
    # Dynamically generate logfile name from the current time
    logtime = time.localtime()
    logfile_name = "embed_log" + str(logtime.tm_year) + "_" + str(logtime.tm_mon) + "_" + str(logtime.tm_mday) + "_" + str(logtime.tm_hour) + str(logtime.tm_min) + str(logtime.tm_sec) + ".txt"
    print("Logfile name is: " + logfile_name)
    # Turn the dictionary into a pandas dataframe
    log_df = pd.DataFrame.from_dict(data = file_dict, orient = 'columns')
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
                    loc_deg = math.floor(input)
                    input = (input - loc_deg)*60
                    loc_min = math.floor(input)
                    input = (input - loc_min)*60
                    loc_sec = round(input, 5)
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
                    loc_deg = math.floor(input)
                    input = (input - loc_deg)*60
                    loc_min = math.floor(input)
                    input = (input - loc_min)*60
                    loc_sec = round(input, 5)
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
    # return the file list updated with the converted DMS values
    return file_list     

# Add location data to the matched files as EXIF fields
def exifWrite(fmatched):
    # Init the image array. Stores binary image data read from file.
    imageArr = []
    # Iterate over the matched image array, opening an image and appending to the image array upon each iteration.
    for img_data in fmatched:
        with open(img_data["filename"], "wb") as img_file:
            imageArr.append(exif.Image(img_file))
    # Iterate in parallel over the image array and the matched image array, fetching and setting EXIF field values for each respective image.       
    for image, img_data in zip(imageArr, fmatched):
        tag_data = img_data["imageloc"]
        image.set("gps_latitude", (tag_data["lat"]["degrees"], tag_data["lat"]["minutes"], tag_data["lat"]["seconds"]))
        image.set("gps_latitude_ref", tag_data["lat"]["direction"])
        image.set("gps_longitude", (tag_data["lon"]["degrees"], tag_data["lon"]["minutes"], tag_data["lon"]["seconds"]))
        image.set("gps_longitude_ref", tag_data["lon"]["direction"])
        # Print the recently set attributes to stdout for verification
        print("Image " + img_data["filename"] + " attributes set:")
        print("Lat: " + image.get("gps_latitude") + " " + image.get("gps_latitude_ref") + " Lon: " + image.get("gps_longitude") + " " + image.get("gps_longitude_ref"))
    # Iterate over the image and matched image arrays in parallel, writing the modified image files to disk
    for image, img_data in zip(imageArr, fmatched):
        with open(img_data["filename"], 'wb') as write_img:
            write_img.write(image.get_file(), )
            
#############################################################################
# THINGS THAT NEED TO BE DONE:
#
# TODO: Create a sample CSV file and test operation of individual functions.
# TODO: Test embedding of data into a sample image.
# TODO: Discuss functions with team.

def main():
    # Enumerate images, their paths, and their associated coordinates
    image_dict = fileEnum("sample_imagecoords.csv", ".\\test_embed_images")
    # Log the results of the matching operation to file
    logResults(image_dict)
    # Get the found files from the dictionary
    #matched_list = image_dict["matched"]
    # Update the location coordinates in the list to be DMS instead of decimal degrees
    #updated_list = locUpdater(matched_list)
    # Write the new coordinates to the image files
    #exifWrite(updated_list)
    
main()