import numpy as np
import cv2 as cv
import glob

template = cv.imread("images_toClean/cateye.jpg", 0)
img_colour = cv.imread("images_toClean/ragdoll.jpg") 
img = cv.imread("images_toClean/ragdoll.jpg", 0) 


#TM_CCORR incorrect result for cat eye test
methods = [cv.TM_CCOEFF, cv.TM_CCOEFF_NORMED, cv.TM_CCORR,
           cv.TM_CCORR_NORMED, cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED]



#iterate and use each comparison method
def matchImages(curtemplate, curImg, curImg_c):
    h, w = curtemplate.shape
    
    for method in methods:
        img2 = curImg.copy()
        img2_colour = curImg_c.copy()
        
        result = cv.matchTemplate(img2, curtemplate, method)
        #minMaxLoc finds the minimum and maximum values in an array and their positions.
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        print(min_loc, max_loc)
        
        #print(result.)
        if(method in [cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED]):
            top_left = min_loc
        else:
            top_left = max_loc
        
        bottom_right = (top_left[0] + w, top_left[1] + h) 
        cv.rectangle(img2_colour, top_left, bottom_right, [0, 0, 255], 5)
        cv.imshow('Match', img2_colour)
        cv.waitKey(0)
        cv.destroyAllWindows()
     
                
matchImages(template, img, img_colour)



