# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 16:43:10 2023

@author: Uriel Martinez-Hernandez

Description: Graphical User Interface with the following features:
            - Serial communication with Arduino
            - Calibration of robot head (set the home position)
            - Control stepper motors of the robot head
            - Open the left and right cameras (eyes) of the robot
"""

import sys
import cv2
from threading import Thread, Lock
import threading
import time
import serial
import serial.tools.list_ports
import string


from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QSlider
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QRadioButton
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QSize


class ControlWindow(QWidget):
    def __init__(self, *args):
        super(QWidget, self).__init__()
        grid = QGridLayout()
        grid.addWidget(self.connectionGroup(), 0, 0)
        grid.addWidget(self.calibrationGroup(), 0, 1)
        grid.addWidget(self.motorControlGroup(), 0, 2)
        grid.addWidget(self.visionGroup(), 0, 3)
        grid.addWidget(self.audioGroup(), 0, 4)
        self.setLayout(grid)        
        
        self.setWindowTitle('BEATRIX Motor GUI - v1.0')
        self.resize(1200, 250)
        self.setFixedSize(QSize(1200,250))

        
        self.show()
        self.stopped = False
        self.leftCameraOpened = False
        self.rightCameraOpened = False
        
    def closeEvent(self, event):
        if self.arduino.isOpen():
            self.arduino.close()

        if self.leftCameraOpened:
            wname = self.video_getter_left.windowNameStr
            print(wname)
            self.video_getter_left.stop()
#            cv2.destroyWindow(wname)

        if self.rightCameraOpened:
            wname = self.video_getter_right.windowNameStr
            print(wname)
            self.video_getter_right.stop()
#            cv2.destroyWindow(wname)
            
        print("manually closed")

    def connectionGroup(self):
            groupBox = QGroupBox("Connection")

            self.arduino = serial.Serial()
            self.comPort_box = QComboBox(self)
    
            ports = serial.tools.list_ports.comports(include_links=False)
            for port in ports :
                print(port.device)
                self.comPort_box.addItem(port.device)
            self.comPort_box.addItem('')


            commsLayout = QFormLayout()
            comBaudrate_label = QLabel("Baudrate:")
            self.comBaudrate_line = QLineEdit("9600")
            comPort_label = QLabel("Port:")
            self.comPortRefresh_button = QPushButton("Refresh ports")
            comPortV1 = QVBoxLayout()
            comPortV1.addWidget(self.comPort_box)
            comPortV1.addWidget(self.comPortRefresh_button)
            self.portConnect_button = QPushButton("Connect")
            self.portDisconnect_button = QPushButton("Disconnect")
            portStatus_label = QLabel("Port status:")
            self.portStatus_status = QLabel("Disconnected")
            
            self.comPortRefresh_button.clicked.connect(self.refreshPorts)
            self.portConnectStatus = False
            self.portConnect_button.clicked.connect(self.portConnection)
            self.portConnect_button.setEnabled(True)
            self.portDisconnect_button = QPushButton('Disconnect')
            self.portDisconnect_button.setEnabled(False)
            self.portDisconnect_button.clicked.connect(self.portConnection)            

            commsLayout.addRow(comBaudrate_label, self.comBaudrate_line)
            commsLayout.addRow(comPort_label, comPortV1)
            commsLayout.addRow(self.portConnect_button, self.portDisconnect_button)
            commsLayout.addRow(portStatus_label, self.portStatus_status)

            groupBox.setLayout(commsLayout)
    
            return groupBox
        
    def calibrationGroup(self):
            groupBox = QGroupBox("Calibration")
    
            self.systemCalibrated = False
            calibrationLabel = QLabel("Status:")
            self.calibrationStatus = QLabel('NOT calibrated')

            self.calibrateButton = QPushButton('Calibrate robot neck')
            self.calibrateButton.setEnabled(False)                
            self.calibrateButton.clicked.connect(self.calibrateMotorSystem)

            self.homePositionButton = QPushButton('Home position')
            self.homePositionButton.setEnabled(False)
            self.homePositionButton.clicked.connect(self.moveToHomePosition)
            
            commsLayout = QFormLayout()
            commsLayout.addRow(calibrationLabel, self.calibrationStatus)
            commsLayout.addRow(self.calibrateButton)
            commsLayout.addRow(self.homePositionButton)
            groupBox.setLayout(commsLayout)
    
            return groupBox

    def motorControlGroup(self):
            groupBox = QGroupBox("Motor control")
    
            self.positiveXLabel = QLabel("Motor X step size:")
            self.positiveXLineEdit = QLineEdit("0")
            self.positiveXButton = QPushButton('go')
            self.positiveXButton.setEnabled(False)
            motorXGroup1 = QHBoxLayout()
            motorXGroup1.addWidget(self.positiveXLineEdit)
            motorXGroup1.addWidget(self.positiveXButton)
            self.positiveXButton.clicked.connect(self.movePositiveXPosition)
            self.positiveYLabel = QLabel("Motor Y step size:")
            self.positiveYLineEdit = QLineEdit("0")
            self.positiveYButton = QPushButton('go')
            self.positiveYButton.setEnabled(False)
            motorYGroup1 = QHBoxLayout()
            motorYGroup1.addWidget(self.positiveYLineEdit)
            motorYGroup1.addWidget(self.positiveYButton)
            self.positiveYButton.clicked.connect(self.movePositiveYPosition)
            self.positiveZLabel = QLabel("Motor Z step size:")
            self.positiveZLineEdit = QLineEdit("0")
            self.positiveZButton = QPushButton('go')
            self.positiveZButton.setEnabled(False)
            motorZGroup1 = QHBoxLayout()
            motorZGroup1.addWidget(self.positiveZLineEdit)
            motorZGroup1.addWidget(self.positiveZButton)
            self.positiveZButton.clicked.connect(self.movePositiveZPosition)

            commsLayout = QFormLayout()
            commsLayout.addRow(self.positiveXLabel, motorXGroup1)
            commsLayout.addRow(self.positiveYLabel, motorYGroup1)
            commsLayout.addRow(self.positiveZLabel, motorZGroup1)
            groupBox.setLayout(commsLayout)
    
            return groupBox


    def visionGroup(self):
        groupBox = QGroupBox("Cameras")

        self.cameraSelectionLabel = QLabel("Select camera")
        self.leftCameraCheckBox = QCheckBox("Left camera")       
        self.leftCameraCheckBox.setChecked(False)
        self.rightCameraCheckBox = QCheckBox("Right camera")       
        self.rightCameraCheckBox.setChecked(False)
        self.openCameraButton = QPushButton("Open camera")
        self.openCameraButton.clicked.connect(self.openCamera)

        commsLayout = QFormLayout()
        commsLayout.addRow(self.cameraSelectionLabel)
        commsLayout.addRow(self.leftCameraCheckBox, self.rightCameraCheckBox)
        commsLayout.addRow(self.openCameraButton)

        groupBox.setLayout(commsLayout)

        return groupBox


    def audioGroup(self):
            groupBox = QGroupBox("Microphones")
    
            vbox = QVBoxLayout()
            groupBox.setLayout(vbox)
    
            return groupBox

        
    def refreshPorts(self):
       self.comPort_box.clear()
       ports = serial.tools.list_ports.comports(include_links=False)

       for port in ports:
           print(port.device)
           self.comPort_box.addItem(port.device)
       self.comPort_box.addItem('')


    def portConnection(self):
        if not self.portConnectStatus:
            self.arduino.port = self.comPort_box.currentText()
            self.arduino.baudrate = self.comBaudrate_line.text()
            self.arduino.open()
            if self.arduino.isOpen():
                self.portConnectStatus = True
                self.portConnect_button.setEnabled(False)
                self.portDisconnect_button.setEnabled(True)
                self.comPort_box.setEnabled(False)
                self.comBaudrate_line.setEnabled(False)
                self.portStatus_status.setText("Connected")
                self.comPortRefresh_button.setEnabled(False)                
                
                time.sleep(0.5)
                self.calibrateButton.setEnabled(True)

        else:
            self.arduino.close()
            if not self.arduino.isOpen():
                self.portConnectStatus = False
                self.portConnect_button.setEnabled(True)
                self.portDisconnect_button.setEnabled(False)
                self.comPort_box.setEnabled(True)
                self.comBaudrate_line.setEnabled(True)
                self.portStatus_status.setText("Disconnected")

                self.systemCalibrated = False
                self.calibrationStatus.setText('NOT calibrated')

                #self.manualMotorControl_home_button.setEnabled(False)
                #self.processControl_start_button.setEnabled(False)
                #self.processControl_stop_button.setEnabled(False)
                self.comPortRefresh_button.setEnabled(True)
                self.calibrateButton.setEnabled(False)
                self.homePositionButton.setEnabled(False)
                self.positiveXButton.setEnabled(False)
                self.positiveYButton.setEnabled(False)
                self.positiveZButton.setEnabled(False)


    def calibrateMotorSystem(self):
        if self.arduino.isOpen():
            command = '@CALNOW\r'
            self.arduino.write(command.encode(encoding='utf-8'))
            self.msg = self.arduino.readline().decode()
            print(self.msg)
            self.msg = self.arduino.readline().decode()
            print(self.msg)
                        
            self.calibrationStatus.setText('System calibrated')
            #self.manualMotorControl_home_button.setEnabled(True)
            #self.processControl_start_button.setEnabled(True)
            #self.processControl_stop_button.setEnabled(True)
            self.homePositionButton.setEnabled(True)
            self.positiveXButton.setEnabled(True)
            self.positiveYButton.setEnabled(True)
            self.positiveZButton.setEnabled(True)
            self.systemCalibrated = True            
        else:
            print("Port is not opened")


    def moveToHomePosition(self):
        if self.arduino.isOpen():
            if self.systemCalibrated:
                        
                self.calibrationStatus.setText('System calibrated')
                
                command = '@MOVHOME\r'
                self.arduino.write(command.encode(encoding='utf-8'))
                self.msg = self.arduino.readline().decode()
                print(self.msg)
                self.msg = self.arduino.readline().decode()
                print(self.msg)
            else:
                print("System not calibrated")
            
        else:
            print("Port is not opened")


    def movePositiveXPosition(self):
        if self.arduino.isOpen():
            if self.systemCalibrated:
                stepValue = self.positiveXLineEdit.text()
                command = '@MOVRX ' + stepValue  +  ' 200\r'
                print(command)
                self.arduino.write(command.encode(encoding='utf-8'))
                self.msg = self.arduino.readline().decode()
                print(self.msg)
                self.msg = self.arduino.readline().decode()
                print(self.msg)
            else:
                print("System not calibrated")
            
        else:
            print("Port is not opened")


    def movePositiveYPosition(self):
        if self.arduino.isOpen():
            if self.systemCalibrated:                        
                stepValue = self.positiveYLineEdit.text()
                command = '@MOVRY ' + stepValue  +  ' 200\r'
                print(command)
                self.arduino.write(command.encode(encoding='utf-8'))
                self.msg = self.arduino.readline().decode()
                print(self.msg)
                self.msg = self.arduino.readline().decode()
                print(self.msg)
            else:
                print("System not calibrated")
            
        else:
            print("Port is not opened")


    def movePositiveZPosition(self):
        if self.arduino.isOpen():
            if self.systemCalibrated:                        
                stepValue = self.positiveZLineEdit.text()
                command = '@MOVRZ ' + stepValue  +  ' 200\r'
                print(command)
                self.arduino.write(command.encode(encoding='utf-8'))
                self.msg = self.arduino.readline().decode()
                print(self.msg)
                self.msg = self.arduino.readline().decode()
                print(self.msg)
            else:
                print("System not calibrated")
            
        else:
            print("Port is not opened")


    def openCamera(self):
        leftCameraSelection = self.leftCameraCheckBox.isChecked()
        rightCameraSelection = self.rightCameraCheckBox.isChecked()

        if ((leftCameraSelection == False) and (rightCameraSelection == False)):
            print("Select a camera to start...")
        else:
            if leftCameraSelection:
                self.video_getter_left = VideoGet('left camera', 1).start()
                self.leftCameraOpened = True

            if rightCameraSelection:
                self.video_getter_right = VideoGet('right camera', 2).start()
                self.rightCameraOpened = True

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
#                if not self.grabbed:
#                    self.stop()
#                else:
                self.grabbed, self.frame = self.stream.read()
                self.img1 = cv2.resize(self.frame,(360,240))
                #if (self.frame):
                cv2.imshow(self.windowNameStr, self.img1)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            if (self.stream):
                self.stream.release()
                cv2.destroyWindow(self.windowNameStr)
           
            break
    
    
    def stop(self):
#        print("stop call")
#        cv2.destroyWindow(self)
        self.stopped = True

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ControlWindow()
    sys.exit(app.exec_())