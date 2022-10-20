### Authors: Jonothan Ridgway 102119636, Tyler Smith 100039114
### save image script to take images and save them


import cv2
import time

_framerate = 30

def gstreamer_pipeline(
    sensor_id=0,
    wbmode=1,
    aelock='false',
    capture_width=1920,
    capture_height=1080,
    display_width=1024,
    display_height=1024,
    framerate=_framerate,
    flip_method=0,
):
    return (
        "nvarguscamerasrc aelock=%s wbmode=%d sensor-id=%d !"
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            aelock,
            wbmode,
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )


def show_camera():

    # To flip the image, modify the flip_method parameter (0 and 2 are the most common)
	print(gstreamer_pipeline(flip_method=0))
	video_capture = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
	
	if video_capture.isOpened():
		try:
			time.sleep(2)
			i = 0		
			while True:
				if i % _framerate == 0:
					ret_val, frame = video_capture.read()
					cv2.imwrite("output/"+str(i/_framerate)+".png", frame)
				time.sleep(1/_framerate)
				i+=1
				if i == _framerate*100:
					break
				
		finally:
			video_capture.release()

	else:
		print("Error: Unable to open camera")


if __name__ == "__main__":
    show_camera()
