import numpy as np
import cv2 as cv
import glob
import imutils

image_paths = glob.glob('hashClean/*.png')
images = []


for image in image_paths:
    img = cv.imread(image)
    images.append(img)


imageStitcher = cv.Stitcher_create()

error, stitched_img = imageStitcher.stitch(images)

if not error:

    cv.imwrite("stitchedOutput.png", stitched_img)
    cv.imshow("Stitched Img", stitched_img)
    cv.waitKey(0)

    stitched_img = cv.copyMakeBorder(stitched_img, 10, 10, 10, 10, cv.BORDER_CONSTANT, (0,0,0))

    gray = cv.cvtColor(stitched_img, cv.COLOR_BGR2GRAY)
    thresh_img = cv.threshold(gray, 0, 255 , cv.THRESH_BINARY)[1]

    cv.imshow("Threshold Image", thresh_img)
    cv.waitKey(0)

    contours = cv.findContours(thresh_img.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    contours = imutils.grab_contours(contours)
    areaOI = max(contours, key=cv.contourArea)

    mask = np.zeros(thresh_img.shape, dtype="uint8")
    x, y, w, h = cv.boundingRect(areaOI)
    cv.rectangle(mask, (x,y), (x + w, y + h), 255, -1)

    minRectangle = mask.copy()
    sub = mask.copy()

    while cv.countNonZero(sub) > 0:
        minRectangle = cv.erode(minRectangle, None)
        sub = cv.subtract(minRectangle, thresh_img)


    contours = cv.findContours(minRectangle.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    contours = imutils.grab_contours(contours)
    areaOI = max(contours, key=cv.contourArea)

    cv.imshow("minRectangle Image", minRectangle)
    cv.waitKey(0)

    x, y, w, h = cv.boundingRect(areaOI)

    stitched_img = stitched_img[y:y + h, x:x + w]

    cv.imwrite("stitchedOutputProcessed.png", stitched_img)

    cv.imshow("Stitched Image Processed", stitched_img)

    cv.waitKey(0)



else:
    print("Images could not be stitched!")
    print("Likely not enough keypoints being detected!")