# Dataset Generation scripts and methods

This documents the scripts used for dataset generation and processing.

## Required Software
- Python (3.9+)
- Google Earth Pro

## Language Definitions
- KML file: A file format used to display geographic data based on the XML standard
- Capture Area: A grid of locations originating from a central origin where each each location drone and satellite images are captured

## Generation Pipeline Overview
1. Use kml_generation.py to generate the KML files
2. Use google earth pro to generate images
3. Use long_tour_process.py to processes images 
4. Use dataset_formatter.py to format dataset for ImageFolder object parsing
5. Use train_test_split.py to split the testing data

## [kml_generation.py](kml_generation.py)
This script generates a number of KML files that are run in google earth pro to generate images. The script assumes the presence of a `kml` folder to store the generated .kml files in. In `kml` a folder `img` with solid color images may be used if the attribute `--delimiter` is used. These images are included in the repo.

The script takes a KML file containing a set of pins as input. This method was chosen due to the ease of placing markers within google earth pro. 

### Arguments:
`--path <path>`<br>
This is the location of the KML file containing the set of input pins. By default this value is a windows user's directory for the inbuilt google earth pro myplaces.kml file.

`--outdir <path>` <br>
This is the directory images are saved into, by default this is `./kml`

`--radius <int>` - <b>Required</b><br>
This is a required attribute. It defines the number of locations that will be used in a grid extending from and not including the central image location

`--altitude <int>` - <b>Required</b><br>
This defines the height satellite images are taken from. The altitude dictates the amount of ground covered by a satellite image which is used to determine the height and location of drone images.

`--name <string>`<br>
This is the name given to the output files. Default value is `tour`

`--duration <int>`<br>
This is the number of seconds the tour spends at each location. This in theory corresponds to the number of images taken at each location however this is unfortunately not the case due to the way google earth pro operates. The default number of images is 10.

`--batchsize <int>`<br>
This is the number of capture areas (grids of captured drone and satellite images based on a single input pin) put into a single KML file. By breaking the file up into smaller batches you allow less repeated work if google earth pro encounters an error. The default batch size is 5.

`--precompute`<br>
This allows the program to cache generated position offsets allowing for much faster repeated generation. This is highly recommended.

`--delimiter`<br>
To allow for easier parsing during image processing, images are used as delimiters to breakup the data. This generates an additional kml file that contains a tour for generating the delimiter images and ground overlays to allow for single color easily recognizable delimiter images.

`--verbose`<br>
This dictates if the program prints actions. May spam console.

`--debug`<br>
This enables certain debug prints. Will spam console, not recommended.

`--pins`<br>
This enables the generation of pins within the KML files. This can help with sanity checking or debugging.

### Command Used:
```
python kml_generation.py --radius 4 --altitude 200 --verbose --precompute --duration 6 --delimiter --path myplaces.kml
```
A radius of 4 and altitude of 200 means approximately 1100 images are taken at each point.

## Generating images from KML files

Once you've used `kml_generation.py` to create your KML files you need to run them through google earth pro.

1. Open google earth pro
2. Setup setting
    - Open tools > options
    - Set cache to max
3. Drag in `delimiter.kml`
4. Open tools > movie maker
5. Run delimiter's tour with these settings:
    - Saved tour: `delimiter.kml`
    - Save the images to: image_folder/delimiter
    - Picture size: 512 x 512
    - 1 frame per second
    - File type: image sequence (.png)
6. Manually pick any two images from image_folder/delimiter, one for each delimiter color
7. Drag in a drone or satellite tour
8. Open tools > movie maker
9. Run tour with same settings as above except:
   - Save to: image_folder/[type]N/[type].png where [type] is drone/sat and N is the number given from KML
10. Repeat 7 through 9 for all drone and satellite KML files
    - You may choose to change the time at which satellite images are taken to allow for variation in color.

## [long_tour_process.py](long_tour_process.py)
This takes the inaccurate output from google earth pro and reduces it to a consistent dataset in a format that can be converted to the final dataset format. This format isolates each capture area and location within the capture area allowing efficient and resilient matching between drone and satellite views. This is done by using perceptual hashing and various steps to isolate and remove poor images from the dataset.

### Process
1. Setup directories
2. Generate a perceptual hash for all images, uses multithreading to minimize compute time
3. Identify any images within the dataset that are substantially distinct. Remove these images.
4. Remove exact duplicate images that are not used as delimiter images.
5. Identify the local similarity of each image to the next image. If an image is substantially similar to the following image, remove the former image.
6. Loop through the image set and divide it according to location and area delimiters.
7. Save data according to the delimiter location and area.

### Arguments
`--name <string>`<br>
Name of the output folder. If this name already exists in the output directory the name will have a timestamp appended.

`--dir <path>`<br>
Name of the input directory this is the directory that is reduced using the script. This is the output directory of running google earth pro kml files.

`--outdir <path>`<br>
Output directory for the cleaned data. By default this is `.\image_folder\out`.

`--delimiterArea <path>`<br>
This is the path to the delimiter that denotes a capture area. By default this is `.\image_folder\delimiter\del-area.png`.

`--delimiterLoc <path>`<br>
This is the path to the delimiter that denotes a location within the capture area. By default this is `.\image_folder\delimiter\del-loc.png`.

`--verbose`<br>
This option determines if the program should print activity. This is recommended as processing can be time consuming and hence

### Command Used:
```
python long_tour_process.py --name [name] --dir ".\image_folder\[name]" --outdir ".\image_folder\out" --delimiterArea ".\image_folder\delimiter\del-area.png" --delimiterLoc ".\image_folder\delimiter\del-loc.png" --verbose
```

This command is run for each folder generated by google earth pro. The output of the command is analyzed to allow for manaual repair of data where possible.

## [dataset_formatter.py](dataset_formatter.py)
This script takes the dataset in the format output by long_tour_generate and transforms it into the data format accpected by the model (follows the ImageFolder format).

### Arguments
`--drone`<br>
This is the directory of a drone folder that has been cleaned using long_tour_process.

`--sat`<br>
This is the directory of the sat folder that matches the drone folder. 

`--outdir`<br>
The output directory of the final formatted dataset.

### Command Used:
```
python dataset_formatter.py --drone ".\image_folder\out\drone1" --sat ".\image_folder\out\sat1" --outdir ".\image_folder\out\formatted"
```
`.\image_folder\out\drone1` & `.\image_folder\out\sat1` are the folders of the related drone and satellite data. `.\image_folder\out\formatted` is the output folder. This command must be run for each set of drone and satellite folders.

## [single_kml_generation.py](single_kml_generation.py)
This script is adapted from long_tour_generate.py and used to generate testing data to support generating satellite data for running the model on real data. It additionally creates a CSV to link location data to output images.

### Arguments
Arguments are the same as long_tour_generate.py however as there is no delimiter used related arguments are also removed.

### Command Used:
```
python .\single_kml_generation.py --radius 4 --altitude 100 --name "mulchXpress" --duration 6 --precompute --verbose --pins
```

## [single_tour_process.py](single_tour_process.py)
This script is used to process the google earth generated from single_kml_generation.py. The actions in this script follow all steps of long_tour_process.py however don't perform delimiter related processing.

### Arguments
Arguments are the same as long_tour_process.py however as there is no delimieter used related arguments are also removed.

### Command Used:
```
python .\single_tour_process.py --name "mulch" --dir ".\image_folder\mulch" --verbose
```

## Other scripts
[filename_increment.py](filename_increment.py)
This script is used for incrementing file names when fixing errors in the dataset after long_tour_process.py

[kml_rename.py](kml_rename.py)
This script is used for renaming pins in KML when creating capture areas. This is important for idenitifing which pins have been detected as overlapping.

[train_test_split.py](train_test_split.py)
This script is used for splitting the training and testing data.

