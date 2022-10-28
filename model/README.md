<h1 align="center"> Optical Guidance System </h1>

This repository contains the dataset link and the code for the original FSRA paper [A Transformer-Based Feature Segmentation and Region Alignment Method For UAV-View Geo-Localization](https://arxiv.org/abs/2201.09206), IEEE Transactions on Circuits and Systems for Video Technology. 

The original repository and dataset are found here:
- https://github.com/Dmmm1997/FSRA
- https://github.com/layumi/University1652-Baseline

## Requirement
1. Download the [OGS-Model](https://liveswinburneeduau-my.sharepoint.com/:f:/g/personal/102117465_student_swin_edu_au/ErNjloBcc1JJucIQT1XiQ-MBnXJpw0GdytrkHYN0JiEf3Q?e=IPXJnm) dataset from the OGS OneDrive folder.
2. Configuring the environment
   * First you need to configure the torch and torchision from the [pytorch](https://pytorch.org/) website
   * ```shell
     pip install -r requirement.txt
     ```

## Train and Test
We provide scripts to complete model training and testing
* Change the **data_dir** and **test_dir** paths in **train_test_local.sh** and then run:
```shell
bash train_test_local.sh
```


The original FSRA model utilised drone, satellite and street images for training and testing. In the context of our optical guidance system, street-view images were not required therefore, the model has been refactored to suit the requirements of the optical guidance system. 
<br><br>
As of publishing the project, the original FSRA model is one year old and, some existing dependencies are outdated and have been superseeded by more efficient technologies. Nvidia Apex is a Pytorch extension which uses automatic mixed precision (AMP) to half the floating point precision from 32 to 16. Reducing the floating point precision, drastically reduces strain on the graphics processing unit (GPU), requiring less video random access memory (VRAM) to train the model and allows the model to be trained by a more diverse range of hardware. As Nvidia Apex is now depreciated and no longer supported, we have removed it and replaced it with Pytorch's new built-in AMP package for FP16.
<br><br>

## Results
The following results compare both, the University1652 and our custom dataset using drone and satellite images only. Each recall value represents as follows:
* Recall@1 - Percentage of true positives where the model correctly guessed the first image
* Recall@5 - Percentage of true positives the model correctly guessed that were within the top 5 images
* Recall@10 - Percentage of true positives the model correctly guessed that were within the top 10 images
<br>

The below image is the testing result of our custom dataset using satellite images from Google earth and, photogrammetry and texture mesh data to simulate drone images. As per our non-functional requirements testing within the test plan document, recall@5 is well above our requirement of 80%, being 89% however, our mean average precision (mAP) is only 54.49% below our requirement of 75%. The mAP is likely low as the small class size may result in certain classes not containing enough significant features to be classified, this means that our dataset may have contained too much sparce, and undulating terrain that could not be correctly classified. 
<br><br>
<p align="center">
<img src="img\customdataset.png"/>
</p>

Comparing our dataset results to the original University1652 dataset, we were very happy that our recall results came as close as they did to those of the orginal dataset. The University1652 dataset likely received a higher mAP due to the training data including many unique buildings to classify.
<br><br>
<p align="center">
<img src="img\UniversityDataset_Results.jpg"/>
</p>


The below heatmap images have been constructed from the test data of our custom dataset. The yellow and red areas within the image, represent a higher number of features compared to surreounding areas. The areas which proved to have more feature points were, buildings and civil infrastructure.
<br><br>
<p align="center">
<img src="img\0114.jpg" width=350 style="margin-right: 15px"/>
<img src="img\0101.jpg" width = 350 style="margin-left: 15px"/>
</p>
