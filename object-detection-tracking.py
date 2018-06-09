# теперь нужно отправить две координаты центра масс объекта

# import the necessary packages

import serial
import struct
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np

ser = serial.Serial('/dev/ttyACM0', 9600) # Yours could be ACM0 or it could be something else.
time.sleep(2)   # this is required because the arduino resets when a serial connection is established

def my_map(x, in_min, in_max, out_min, out_max):
    return int((x-in_min) * (out_max-out_min) / (in_max-in_min) + out_min)

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (320, 240)
camera.framerate = 10
camera.hflip = True

rawCapture = PiRGBArray(camera, size=(320, 240))

# allow the camera to warmup
time.sleep(0.1)

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array

    blur = cv2.blur(image, (3,3))

    #hsv to complicate things, or stick with BGR
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    thresh = cv2.inRange(hsv, np.array((152,168,59)), np.array((180,255,255)))

    #lower = np.array([12,178,61],dtype="uint8")
    #upper = np.array([225,88,50], dtype="uint8")
    #upper = np.array([210,90,70], dtype="uint8")

    # lower_red = np.array([152,168,59])
    # upper_red = np.array([180,255,255])

    # thresh = cv2.inRange(blur, lower, upper)
    thresh2 = thresh.copy()

    # find contours in the threshold image
    image, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
   # contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   # contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # finding contour with maximum area and store it as best_cnt
    max_area = 0
    best_cnt = 10
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > max_area:
            max_area = area
            best_cnt = cnt

    # finding centroids of best_cnt and draw a circle there
    M = cv2.moments(best_cnt)
    posX, posY = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
    #if best_cnt>1:
    if posX == 0 and posY == 0:
        posX = int(camera.resolution[0]/2)
        posY = int(camera.resolution[1]/2)
        
    cv2.circle(blur,(posX,posY),10,(255,0,0),-1)
##    ser.write(struct.pack('>2H', posX, posY))
    mapX = my_map(posX, 0, 320, 0, 255)
    mapY = my_map(posY, 0, 240, 0, 255)

##    if frame % 30 == 0:
##    print(frame)
    ser.write(struct.pack('>2B', mapX, mapY))
##    ser.write(struct.pack('>H', mapX))
##    ser.write(struct.pack('>H', mapY))
##    ser.write(struct.pack('>i', posX))

    print(mapX, mapY)
    # show the frame
    cv2.imshow("Frame", blur)
    #cv2.imshow('thresh',thresh2)
    key = cv2.waitKey(1) & 0xFF

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
