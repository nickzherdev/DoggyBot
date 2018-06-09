# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

import numpy as np
import math
import cmath
 
res_x = 640
res_y = 480

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
# camera.vflip = True
camera.resolution = (res_x, res_y)
camera.framerate = 15
rawCapture = PiRGBArray(camera, size=(res_x, res_y))
 
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

    # for x1,y1,x2,y2 in lines[0]:
    #     cv2.line(line_img,(x1,y1),(x2,y2),(0,0,255), 8)

    # Merge the image with the lines onto the original.
    img = cv2.addWeighted(img, 0.8, line_img, 1.0, 0.0)
    # Return the modified image.
    return img


def pipeline(image):
    """
    An image processing pipeline which will output
    an image with the lane lines annotated.
    """
    setpoint = res_x/2

    height = image.shape[0]
    width = image.shape[1]

    region_of_interest_vertices = [
        (0.25*width, height),
        (width / 2, 0), # height * 0.1
        (0.75*width, height),
    ]

    gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray_image, (7, 7), 0)
    cannyed_image = cv2.Canny(blurred, 180, 300)
    cropped_image = region_of_interest(cannyed_image, np.array([region_of_interest_vertices], np.int32))

    img, contours, hierarchy = cv2.findContours(cropped_image.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)  
    cv2.drawContours(image, contours, -1, (0, 255, 0), 3)
    if len(contours) > 0 :
        blackbox = cv2.minAreaRect(contours[0]) # ( center (x,y), (width, height), angle of rotation )
        # x_blk, y_blk , w_blk, h_blk = cv2.boundingRect(contours[0])

        (x_min, y_min), (w_min, h_min), ang = blackbox

        error = int(x_min - setpoint) 
        ang = int(ang)  

        box = cv2.boxPoints(blackbox)
        box = np.int0(box)
        cv2.drawContours(image,[box],0,(0,255,255),3)
        cv2.line(image, (int(x_min),int(res_y*0.8) ), (int(x_min),int(res_y)), (0,0,255),3)
        cv2.putText(image,"Angle = " + str(math.floor(ang)),(20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (200, 0, 200), 3)
        cv2.putText(image,"Error = " + str(error),(20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (200, 0, 200), 3)
        cv2.line(image, (int(res_x/2), int(res_y*0.8)), (int(res_x/2), int(res_y)),(255,0,0), 3) # verticle middle line

        # line_image = draw_lines(image, lines)

        return image
    else: 
        return image


        # cv2.line(image, (int(x_min + w_min/2), int(y_min)), (int(y_min), int(y_min + h_min)), (255,0,0),3)

        # cv2.rectangle(image, (int(x_min),int(y_min)), (int(x_min+w_min), int(y_min+h_min)), (0,0,255), 3)  # draw rect on found coords
        # cv2.rectangle(image, (int(x_blk),int(y_blk)), (int(x_blk+w_blk), int(y_blk+h_blk)), (0,0,255), 3)  # draw rect on found coords
        # centerx_blk = int(x_min + (w_min/2))
        # cv2.line(image, (centerx_blk, 0), (centerx_blk, res_y),(255,0,0),3) # line from top to bottom on centerx, verticle middle line


    #cropped_image = region_of_interest(cannyed_image, np.array([region_of_interest_vertices], np.int32))
    # lines = cv2.HoughLinesP(cannyed_image,rho = 1,theta = 1*np.pi/180,threshold = 5,minLineLength = 30,maxLineGap = 60)



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