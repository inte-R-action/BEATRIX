# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 00:02:56 2023

@author: umh21
"""

# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time


# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
#greenLower = (29, 86, 6)
greenLower = (40, 140, 6)
greenUpper = (64, 255, 255)
#greenUpper = (64, 255, 255)
#pts = deque(maxlen=args["buffer"])

stream = cv2.VideoCapture(0)

width = stream.get(cv2.CAP_PROP_FRAME_WIDTH)   # float `width`
height = stream.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`
  
print('width: ', width, ', height: ', height)

# allow the camera or video file to warm up
time.sleep(2.0)

# keep looping
while True:
    # grab the current frame
    ret, frame = stream.read()

    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
 
    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        intX = int(x)
        intY = int(y)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        # only proceed if the radius meets a minimum size
        if radius > 80:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (intX, intY), int(radius), (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            
            print('[width, height]: ', frame.shape[0], ',', frame.shape[1], '; centre (x, y):', intX, ', ', intY, '; radius: ', int(radius))

    # update the points queue
    #pts.appendleft(center)

	# show the frame to our screen
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

stream.release()

# close all windows
cv2.destroyAllWindows()