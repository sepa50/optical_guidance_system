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

# Read image files from CSV, and evaluate if they exist or not within a directory and its subdirectories
def fileEnum(csv_file, root_path):
    # Read the CSV file into a dataframe
    coordCSV = pd.read_csv(
        filepath_or_buffer = csv_file,
        sep = ','
    )
    
    # Extract the filenames column from the CSV and store in an array
    satimg_names = coordCSV['FileNames'].values
    satimg_loc = coordCSV["Location"].values
    
    # Evaluate and store the file/directory structure of the root dir and all subdirs
    dir_structure = os.walk(root_path)
    
    # Init arrays to hold the data we need
    found_fnames = []
    found_fpaths = []
    matched_files = []
    unmatched_files = []
    
    # Iterate over the 3-tuples in the dir_structure list and concat all the filenames and paths into two respective lists
    for directory in dir_structure:
        found_fnames.append(directory[2])
        found_fpaths.append(directory[0])

    # Iterate over the filename and path lists in parallel, and sort file names and paths that do/do not match values from the CSV into respective arrays
    for fname, fpath in zip(found_fnames, found_fpaths):
        for iname, iloc in zip(satimg_names, satimg_loc):
            if fname == iname:
                matched_files.append({"filename": fname, "filepath": fpath, "imageloc": iloc})
            else:
                unmatched_files.append({"filename": fname, "filepath": fpath})

    # Return a dict containing the matched and unmatched file arrays
    dict = {"matched": matched_files, "unmatched": unmatched_files}
    return dict

# Log the results of the embedding operation to a CSV
def logResults(file_dict):
    logtime = time.localtime()
    logfile_name = "embed_log" + logtime.tm_year + "_" + logtime.tm_mon + "_" + logtime.tm_mday + "_" + logtime.tm_sec + ".txt"
    log_df = pd.DataFrame(file_dict)
    log_df.to_csv("./" + logfile_name)
    
    
## TODO: Need to figure out how to get location data in the right format. Will need to either change the layout of the CSV or will
# need to do some formatting on a combined lat/lon string to get the right outputs.
## TODO: Need to figure out how I am going to read in the data - how will the location data be associated with an image. I think
# that satimg_loc needs to be a dictionary with the appropriate processed values, meaning that I need to write a function to process
# the location data before I iterate over the lists in parallel.

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
        image.set("gps_latitude", img_data["imageloc"]["gps_lat"])
        image.set("gps_latitude_ref", img_data["imageloc"]["gps_lat_ref"])
        image.set("gps_longitude", img_data["imageloc"]["gps_lon"])
        image.set("gps_longitude_ref", img_data["imageloc"]["gps_lon_ref"])
        # Print the recently set attributes to stdout for verification
        print("Image " + img_data["filename"] + " attributes set:")
        print("Lat: " + image.get("gps_latitude") + " " + image.get("gps_latitude_ref") + " Lon: " + image.get("gps_longitude") + " " + image.get("gps_longitude_ref"))
    # Iterate over the image and matched image arrays in parallel, writing the modified image files to disk
    for image, img_data in zip(imageArr, fmatched):
        with open(img_data["filename"], 'wb') as write_img:
            write_img.write(image.get_file())