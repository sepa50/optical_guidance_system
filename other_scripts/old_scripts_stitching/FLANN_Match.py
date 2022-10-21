import math
import numpy as np
import sys
import cv2 as cv
import matplotlib.pyplot as plt
import glob
            
def addImageToFolder(img, count):
    img_colour = cv.imread(img)
    name = 'sat_' + str(count).zfill(5)
    cv.imwrite(sys.argv[2] + f'/{name}.jpg', img_colour)
    
if len(sys.argv) != 3:
    quit()
    
path_from = glob.glob(sys.argv[1] + "/*.png")
path_to = glob.glob(sys.argv[2] + "/*.png")
print(sys.argv)
percent_limit = 90
count = len(path_to)
i = 0
for image in path_from:
    print("Checking image " + str(image) + "....")
    if len(path_to) < 1:
        path_to.append(image)
        addImageToFolder(image, count)
        count += 1
        continue
    flag = True
    
    while i < count:
        img1 = cv.imread(image,cv.IMREAD_GRAYSCALE)  # queryImage
        img2 = cv.imread(path_to[i],cv.IMREAD_GRAYSCALE) # trainImage
        
        # Initiate SIFT detector
        sift = cv.SIFT_create()

        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(img1,None)
        kp2, des2 = sift.detectAndCompute(img2,None)
        print('Key-points found: ' + str(len(kp2)))
        
        # FLANN parameters
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks=50)   # or pass empty dictionary
        flann = cv.FlannBasedMatcher(index_params,search_params)
        matches = flann.knnMatch(des1,des2,k=2)
        print('Matches: ' + str(len(matches)))
        
       
        
        """
        #imageResult(matches)
        if(len(kp2) > len(matches)):
            percent_match = ((len(matches) / len(kp2)) * 100)
        else:
            percent_match = ((len(kp2) / len(matches)) * 100)
            
        print("Percent Match: " + str(percent_match))
        percent_match = int(percent_match)
        
        if percent_match > percent_limit:
            flag = False 
            break 
        """
        
        i += 1
    #add to new data collection
    
        
    if flag == True:
        print("Adding new image to folder.... \n")
        path_to.append(image)
        addImageToFolder(image, count)
        count += 1
    i = 0
   

#sat1 289