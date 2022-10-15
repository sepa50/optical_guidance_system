import cv2

path = r'/home/jetson/Pictures/Screenshot from 2022-09-13 19-45-27.png'

image = cv2.imread(path)

window_name = 'image'

cv2.imshow(window_name, image)

cv2.waitKey(0)

cv2.destroyAllWindows()
