# Sandbox testing for dataset generation
This is how tested is performed for dataset generation. Due to the difficulty performing automatic validation manual validation is used to verify the functionality of each major script within the dataset generation pipeline.

## KML Generation script - Passed
1. Run test_generation.sh
2. Open google earth pro
3. Open the KML files within `test_kml_output`
4. Validate that delimiter correctly loads images
5. Open the validation KML files within `validate_kml_output`
6. Validate the pins in test_kml_output match the repetition_kml_output pins
7. Validate that the test KML files matches the validation KML file

## KML Generation overlap test - Passed
This test is used to ensure the overlapping detection is functional in long_tour_generate.
1. Run test_overlap.sh
2. Check it throws an exception

## Google earth validation - Passed
This test sequence is used to verify correct functionality of google earth pro when using the generated KML files.

1. Open google earth pro
2. Open KML files located in `validate_kml_output`
3. Run Movie Maker for delimiter into `test_output_google_earth_delimiter` using methodology covered in script documentation
4. Run Movie Maker for drone and satellite images into `test_output_google_earth` using methodology covered in script documentation
5. Check for significant failures in image generation. This may consist of:
    - Grey images
    - Blurry images
    - Delimiter images at improper altitudes
    - Images at improper altitudes

## Image processing - Passed
This is validation of the image processing script long_tour_generate. This also serves to validate the effectiveness of single_tour_process.

Required Software: WizTree

1. Run test_processing.sh
2. Validate the correct number of files were output:
    - 2 Capture Areas
    - 45 Drone images
    - 225 Sat images
3. Open WizTree
4. Using WizTree analyze the number of files produced in the output folder
    - Ensure file numbers match printed file numbers
    - Ensure file sizes are uniform
    - Ensure each capture area contains 9 capture locations

## Dataset Formatting - Passed
This bash script is used for testing the dataset formatting and dataset splitting scripts. These scripts take the formatting that represents the captured structure of the dataset to the format accepted by the PyTorch ImageFolder object.

1. Run test_formatting.sh
2. Check formatting in `test_formatted_dataset` matches the expected structure:
```
drone
    0000
        img1.png ... img5.png
    0001
    ...
    0008

sat 
    0000
        img1.png ... img9.png
    0001
    ...
    0008
```
3. Check `test_split_dataset` matches the expected structure:
```
drone
    0000
        img1.png ... img5.png
    0001
    ...
    0008

sat 
    0000
        img1.png ... img9.png
    0001
    ...
    0008

test-drone
    000X
    ...
    000X
        img1.png ... img5.png

test-sat 
    000X
    ...
    000X
        img1.png ... img9.png
```