# Dataset Generation scripts and methods

This documents the scripts used for dataset generation and processing.

## Required Software
- Python (3.9+)
- Google Earth Pro

## Language Definitions
- KML file: A file format used to display geographic data based on the XML standard
- Capture Area: A grid of locations originating from a central origin where each each location drone and satellite images are captured

## kml_generation.py
This script generates a number of KML files that are run in google earth pro to generate images. The script assumes the presence of a `kml` folder to store the generated .kml files in. In `kml` a folder `img` with solid color images may be used if the attribute `--delimiter` is used. These images are included in the repo.

The script takes a KML file containing a set of pins as input. This method was chosen due to the ease of placing markers within google earth pro. 

### Arguments:
`--radius <int>` - <b>Required</b><br>
This is a required attribute. It defines the number of locations that will be used in a grid extending from and not including the central image location

`--altitude <int>` - <b>Required</b><br>
This defines the height satellite images are taken from. The altitude dictates the amount of ground covered by a satellite image which is used to determine the height and location of drone images.

`--path`<br>
This is the location of the KML file containing the set of input pins. By default this value is a windows user's directory for the inbuilt google earth pro myplaces.kml file.

`--outdir`<br>
This is the directory images are saved into, by default this is `./kml`

`--name`<br>
This is the name given to the output files. Default value is `tour`

`--duration`<br>
This is the number of seconds the tour spends at each location. This in theory corresponds to the number of images taken at each location however this is unfortunately not the case due to the way google earth pro operates. The default number of images is 10.

`--batchsize`<br>
This is the number of capture areas (grids of captured drone and satellite images based on a single input pin) put into a single KML file. By breaking the file up into smaller batches you allow less repeated work if google earth pro encounters an error. The default batch size is 5.

`--delimiter`<br>
To allow for easier parsing during image processing, images are used as delimiters to breakup the data. This generates an additional kml file that contains a tour for generating the delimiter images and ground overlays to allow for single color easily recognizable delimiter images.

`--precompute`<br>
This allows the program to cache generated position offsets allowing for much faster repeated generation. This is highly recommended.

`--verbose`<br>
This dictates if the program prints actions. May spam console.

`--debug`<br>
This enables certain debug prints. Will spam console, not recommended.

## Generating images from KML files

Once you've used `kml_generation.py` to create your KML files you need to run them through google earth pro.

1. Open google earth pro
2. Setup setting
    - Open tools > options
    - Set cache to max
3. Drag in `delimiter.kml`, disable pins
4. Open tools > movie maker
5. Run delimiter's tour with these settings:
    - Saved tour: `delimiter.kml`
    - Save to: image_folder/del/del.png
    - Picture size: 512 x 512
    - 1 frame per second
    - File type: image sequence (.png)
6. Manually pick any two images from image_folder/del, one for each delimiter color
7. Drag in a drone or satellite tour, disable pins
8. Open tools > movie maker
9. Run tour with same settings as above except:
    - Save to: image_folder/[type]N/[type].png where [type] is drone/sat and N is the number given from KML
10. Repeat 7 through 9 for all drone and satellite KML files
    - You may choose to change the time at which satellite images are taken to allow for variation in color.




