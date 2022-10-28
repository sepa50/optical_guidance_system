# Location Embedding Documentation
**Author**: Alex Jennings
**Student ID**: 102117465
**University**: Swinburne University of Technology

## Document Purpose
This document aims to provide an overview of the script used to georeference the satellite image dataset, by storing GPS coordinates within the image EXIF tags.

## Software Requirements
- A Python 3 installation
- Ability to install packages via `pip` or the following libraries preinstalled.
- Python libraries:
	- Pandas `pip install pandas`
		- Handles CSV R/W
	- Pathlib
		- Handles path generation
	- PIL `pip install pil`
		- Handles raw EXIF manipulation
	- Tyf `pip install tyf`
		- Handles EXIF updating

## Key Definitions
- EXIF - Exchangable Image File Format. Allows the embedding of auxillary information within JPEG and TIFF image files.
- DMS - Degrees-Minutes-Seconds. Representation of coordinate angles, method of representing latitude and longitude.
	- DMS Latitude: 0 <= θ <= 90
	- DMS Longitude 0 <= θ <= 180
	- Unsigned value augmented by direction LON:{E,W}, LAT:{N,S}
- Decimal Degrees - Representation of coordinate angles, method of representing latitude and longitude.
	- DD Latitude: -90 <= θ <= 90
	- DD Longitude -180 <= θ <= 180

## location_embed.py
This script performs the georeferencing of the satellite image dataset. The script requires that a list of file names and associated latitude and longitude coordinates are present in a CSV format. This is the master dataset from which the image files have data embedded.

The script contains a number of functions, each performing distinct roles.

### fileEnum
Reads the filenames and coordinates from the master CSV file, and searches down from a root directory to determine the paths of files listed in the CSV. Stores the file path information and the location information in nested dictionaries within a list, to allow iterating over a series of image-information data structures.

The function was written specifically to avoid hard-coded file paths and subsequently improve portability. By searching from a root directory and relying only on the image file names being provided, the embedding operation can be performed irrespective of the underlying directory structure.

**Arguments**
`csv_file` - Required. Specifies location of the master CSV.
`root_path` - Required. Specifies the root path from which to search downwards.

### logResults
Logs the results of the file search operation to file; outputs a CSV of matched and unmatched images. This is to provide concrete feedback to the user and indicate when the embedding operation could/could not be performed on a particular image as it could/could not be found.

**Arguments**
`file_dict` - Required. The organised file dictionary output by fileEnum.

### locConverter
Performs numerical conversion between coordinate systems. Can convert from DMS to Decimal Degrees and vice versa. This script was written with the intent that it could form part of a general-purpose library during future work on the project. Subsequently, there is provision for error handling due to the potential for unsanitised user input in future use cases of the function.

**Arguments**
`input` - Required. The numerical value to convert from.
`type` - Required. Selects if the coordinate is latitude or longitude. Allowable values `"lat"`, `"lon"` as String.
`conversion` - Required. Selects if the conversion is to DMS or Decimal Degrees. Allowable values `"dms"`, `"dec"` as String.

### locUpdater
Iterates over the series of data structures associated with each image, and updates the coordinates to the appropriate system. This function was in use previously when another image manipulation library was in use. Upon switching to another library due to buggy code in the initial library affecting image generation, the requirement for coordinate conversion is presently deprecated. The function was deemed to have application in future project work, and hence remains within the script for future use.

**Arguments**
`file_list` - Required. A list of data structures associated with each image.

### exifWrite
Performs the EXIF tag update operation for images that have a confirmed match in the filesystem. Opens the image, updates the EXIF tag values and then saves the image to disk.

**Arguments**
`matched_images` - Required. List of images that were successfully matched by fileEnum.

### main
The main function that runs and calls other functions within the script. Called upon script execution by the Python interpreter. Does not take arguments, only executes function calls and passes control to the called subroutines.

**Arguments**
None.

## Frequently Asked Questions
### Why EXIF?
The EXIF standard allows for embedding of extra data associated with an image into the image file itself. The result is a single binary file, from which auxillary attributes can be access by navigating to the EXIF portion of the file adjacent to the image data. Embedding of the GPS coordinates into the satellite images themselves as a single source of truth was chosen after consideration of other data storage options, including semi-structured formats including JSON and XML, relational DBMS solutions such as MySQL, and hybrid No-SQL solutions such as MongoDB.

### Why not JSON/MySQL/MongoDB/etc?

MySQL, a relational database, was chosen as the intial solution whilst developing the script, with research being performed into SQL DML and query formulation. After preliminary design work, it was realised that the DBMS would place significant overhead on the Jetson, and since the image count for the proof-of-concept was not large enough to justify a consolidated DBMS solution.

JSON and XML were subsequently considered, due to their portability and cross-platform potential. Following research, it was determined that they had significant downsides, owing to dififculty in appending information or modifying the storage structure after the initial data was written. MongoDB was identified as another potential solution and preliminary research was performed.

Finally, the idea that location data could be innately associated with each image was formed. Embedding within EXIF fields was brainstormed as the best solution, with the added benefit of innate portability of information - the images are required for successful matching to occur and subsequently underpins the bulk of the project. By associating the data directly with objects for which integrity must be all but guaranteed, the association subsequently provides assurance for the integrity of the associated information. This distributed nature of information storage provides significantly greater redundancy compared to having location data stored in a unified database, thereby constituting a single point-of-failure.