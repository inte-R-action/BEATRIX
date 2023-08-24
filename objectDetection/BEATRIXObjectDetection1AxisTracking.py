# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 01:03:44 2023

@author: umh21
"""

# steps
# 1 - connect BEATRIX to Arduino COM port
# 2 - manually define the home position
# 3 - enable motors
# 4 - calibrate motors to set the home position
# 5 - connect the camera (only left or right camera)
# 6 - enable ball detection
# 7 - enable tracking the ball in 1 axis at the time




# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import serial
from threading import Thread, Lock


"""
1 - connect BEATRIX to Arduino via COM port
"""

arduino = serial.Serial()
arduino.port = 'COM4'
arduino.baudrate = '9600'

if not arduino.isOpen():
    arduino.open()
    if arduino.isOpen():
        print("Arduino opened correctly")
    else:
        print("Error Arduino couldn't open")        

time.sleep(2)
    
"""
2 - manually define the home position
"""
# Set the home position for the robot head manually


"""
3 - enable motors
"""

command = '@ENMOTORS ON\r'
systemCalibrated = False
arduino.write(command.encode(encoding='utf-8'))
#msg = arduino.readline().decode()
#print(msg)
#msg = arduino.readline().decode()
#print(msg)

time.sleep(2)


"""
4 - calibrate motors to set the home position
"""

command = '@CALNOW\r'
arduino.write(command.encode(encoding='utf-8'))
#msg = arduino.readline().decode()
#print(msg)
#msg = arduino.readline().decode()
#print(msg)

time.sleep(2)


# Class implemented to start video from cameras in a thread without blocking robot actions
class VideoGet:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self, windowName='video', src=0):
        self.stream = cv2.VideoCapture(src)
        self.grabbed, self.frame = self.stream.read()
        self.stopped = False
        self.windowNameStr = windowName

    def start(self):
        Thread(target=self.get, args=()).start()
        return self
    
    def get(self):
        while True:
            while not self.stopped:
                self.grabbed, self.frame = self.stream.read()
                self.img1 = cv2.resize(self.frame,(360,240))
                cv2.imshow(self.windowNameStr, self.img1)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            if (self.stream):
                self.stream.release()
                cv2.destroyWindow(self.windowNameStr)
           
            break    
        
    def stop(self):
        self.stopped = True


"""
5 - connect the camera (only left or right camera)
"""

video_getter_right = VideoGet('left camera', 0).start()
cameraOpened = True


time.sleep(5)


command = '@ENMOTORS OFF\r'
systemCalibrated = False
arduino.write(command.encode(encoding='utf-8'))

if arduino.isOpen():
    arduino.close()
    print("Arduino closed correctly")

video_getter_right.stop()

