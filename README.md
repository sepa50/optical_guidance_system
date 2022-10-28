# Optical Guidance System

## Overview 

The purpose of the Optical Guidance system is to provide a self-contained Geolocalisation solution for unmanned aerial vehicles (UAVs), allowing for self-localisation in GPS-denied environments. The system was developed to be deployed as a vehicle payload, with all necessary logic outsourced to the payload computer. To the UAV flight controller, the system appears functionally the same as a GPS module – and that is where the power of the system lies. 

The system core is an NVIDIA Jetson Nano, which runs the machine learning model and processes images from the on-board camera. Images are captured whilst in flight, with the machine learning model classifying them on-the-fly and returning the most likely match. The geospatial data associated with the image is subsequently passed to the flight controller, analogous to a GPS module. 

The end result is a system that provides synthesized GPS coordinates to a UAV, whilst requiring only clear visuals of the ground beneath the drone. 

### Repository Contents 

The repository consists of: 

- Scripts to run on the Jetson to run the system and communicate with the UAV 

- Scripts to run train and test the model 

- Scripts to generate a dataset using google earth photogrammetry for drone images and google earth satellite images for reference images 

- Scripts to embedding the location of the satellite images within the images 

## Documentation

[Model documentation](model/)

[Jetson code documentation](jetson_code/)

[Dataset generation documentation](dataset_generation/)

[Dataset generation testing documentation](dataset_generation/testing_model_generation/)

[Location embedding documentation](location_embedding/)

## Quick Start Guide

### Hardware Used

- Jetson Nano 2GB
- STARVIS IMX412
- Drone/UAV
    - PX4FLOW
    - Pixhawk Cube or other flight controller
    - GPS
    - Herelink

### Running the System

Gather up-to-date satellite imagery of the test area and embed the location within the images.

Install pretrained model on the Jetson Nano and add the satellite imagery of the area to be tested.

Connect the Jetson Nano with the camera attached to the drone and power it with a power supply that supplies 5V and at least 3A.

Setup the parameters on the drone as specified [here](jetson_code/README.md).

Launch the drone with the system attached.
