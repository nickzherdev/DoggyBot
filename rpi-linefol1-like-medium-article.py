# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

import numpy as np
import math
 
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
# camera.vflip = True
camera.resolution = (640, 480)
camera.framerate = 15
rawCapture = PiRGBArray(camera, size=(640, 480))
 
# allow the camera to warmup
time.sleep(0.1)

def region_of_interest(img, vertices):
    mask = np.zeros_like(img)
    match_mask_color = 255
    cv2.fillPoly(mask, vertices, match_mask_color)
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def draw_lines(img, lines, color=[255, 0, 0], thickness=3):
    # Make a copy of the original image.
    img = np.copy(img)
    # Create a blank image that matches the original in size.
    line_img = np.zeros(
        (
            img.shape[0],
            img.shape[1],
            3
        ),
        dtype=np.uint8,
    )
    # Loop over all lines and draw them on the blank image.
    for x1,y1,x2,y2 in lines[0]:
        cv2.line(line_img,(x1,y1),(x2,y2),(0,255,0), 3)

    # Merge the image with the lines onto the original.
    img = cv2.addWeighted(img, 0.8, line_img, 1.0, 0.0)
    # Return the modified image.
    return img


def pipeline(image):
    """
    An image processing pipeline which will output
    an image with the lane lines annotated.
    """

    height = image.shape[0]
    width = image.shape[1]

    region_of_interest_vertices = [
        (0.25*width, height),
        (width / 2, 0), # height * 0.1
        (0.75*width, height),
    ]

    gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray_image, (7, 7), 0)
    cannyed_image = cv2.Canny(blurred, 30, 140)
    cropped_image = region_of_interest(cannyed_image, np.array([region_of_interest_vertices], np.int32))
  #  lines = cv2.HoughLinesP(cropped_image,rho = 1,theta = 1*np.pi/180,threshold = 180,minLineLength = 200,maxLineGap = 70)
    lines = cv2.HoughLinesP(cropped_image,rho = 1,theta = 1*np.pi/180,threshold = 10,minLineLength = 50,maxLineGap = 30)
    
    if lines is not None:
        line_image = draw_lines(image, lines)
        return line_image
    else: 
        return image

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array # This method returns a frame from the video stream. 
                        # The frame then has an array property, which corresponds 
                        # to the frame  in NumPy array format
    
    
    # show the frame
    cv2.imshow("Frame", pipeline(image))
    key = cv2.waitKey(1) & 0xFF # what is 0xFF ?
 
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0) # You must clear the current frame before you move on to the next one!
 
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break