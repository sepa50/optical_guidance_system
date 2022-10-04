

###gstreamer options for camera
def gstreamer_pipeline(
    sensor_id=0,
    wbmode=1,
    aelock='false',
    capture_width=1920,
    capture_height=1080,
    display_width=1024,
    display_height=1024,
    framerate=30,
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
