#!/usr/bin/python3

import cv2
import numpy as np
from datetime import datetime
import time

class MotionDetectorAdaptative():

    def onChange(self, val): #callback when the user change the detection threshold
        self.threshold = val

    def __init__(self, threshold=10, doRecord=True, showWindows=True, camId=0):
        self.writer = None
        self.font = None
        self.doRecord = doRecord #Either or not record the moving object
        self.show = showWindows #Either or not show the 2 windows
        self.frame = None
        self.frame_rate = 120
        self.frame_width = 1280
        self.frame_height = 720

        self.capture = cv2.VideoCapture(camId)
        self.frame = self.capture.read() #Take a frame to init recorder
        # if doRecord:
        #     self.initRecorder()
        self.gray_frame = np.zeros((self.frame_height,self.frame_width,1), np.uint8)
        self.average_frame = np.zeros((self.frame_height,self.frame_width,3), np.float32)
        self.absdiff_frame = None
        self.previous_frame = None

        self.surface = self.frame_width * self.frame_height
        self.currentsurface = 0
        self.currentcontours = None
        self.threshold = threshold
        self.isRecording = False
        self.motionDetected = False
        self.trigger_time = 0 #Hold timestamp of the last detection

        if showWindows:
            cv2.namedWindow("Image")
            cv2.createTrackbar("Detection treshold: ", "Image", self.threshold, 100, self.onChange)

    def initRecorder(self): #Create the recorder
        codec = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
        self.writer = cv2.VideoWriter(datetime.now().strftime("%b-%d_%H_%M_%S")+".avi", codec, self.frame_rate, (self.frame_width, self.frame_height))
        # FPS set to 5 because it seems to be the fps of my cam but should be ajusted to your needs
        # self.font = cv2.putText(cv2.FONT_HERSHEY_SIMPLEX,(0,0),(511,511),(255,0,0),5) #Creates a font

    def run(self, cam):
        started = time.time()
        while True:
            self.capture.grab()
            result, img = self.capture.retrieve()
            # img = self.capture.read()[0]

            instant = time.time() #Get timestamp o the frame
            height, width = img.shape[:2]
            scaling_factor_x = float(self.frame_width) / width #Camera aspect ratio may vary
            scaling_factor_y = float(self.frame_height) / height
            res_img = cv2.resize(img, None, fx=scaling_factor_x, fy=scaling_factor_y, interpolation = cv2.INTER_NEAREST)
            self.processImage(res_img) #Process the image
            self.somethingHasMoved() #Run this to update self.motionDetected

            if not self.isRecording:
                if self.motionDetected:
                    self.trigger_time = instant #Update the trigger_time
                    if instant > started + 20: #Wait 3 second after the webcam start for luminosity adjusting etc..
                        print("Something is moving !")
                        if self.doRecord: #set isRecording=True only if we record a video
                            self.isRecording = True
                            self.initRecorder()
                cv2.drawContours(res_img, self.currentcontours, -1, (0, 0, 255), 3)
            else:
                if instant >= self.trigger_time + 2 and not self.motionDetected: #Record during 5 seconds
                    print("Stop recording")
                    self.isRecording = False
                    self.writer.release()
                else:
                    # cv.PutText(currentframe,datetime.now().strftime("%b %d, %H:%M:%S"), (25,30),self.font, 0) #Put date on the frame
                    self.writer.write(res_img) #Write the frame

            if self.show:
                if self.motionDetected:
                    cv2.putText(res_img, "Motion Detected", (20,400), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                cv2.imshow("Image", res_img)
                # cv2.imshow("Gray", self.gray_frame)

            c = cv2.waitKey(1) % 0x100
            if c == 27 or c == 10: #Break if user enters 'Esc'.
                break

    def processImage(self, curframe):
            curframe = cv2.blur(curframe, (8,8))
            if self.absdiff_frame is None: #For the first time put values in difference, temp and moving_average
                self.absdiff_frame = curframe.copy()
                self.previous_frame = curframe.copy()
                self.average_frame = np.float32(curframe) #Should convert because after runningavg take 32F pictures
            else:
                # Generate moving average image if needed
                if self.average_frame is None:
                    self.average_frame = np.float32(curframe)
                cv2.accumulateWeighted(curframe, self.average_frame, 0.03) #Compute the average

            self.absdiff_frame = cv2.absdiff(curframe, cv2.convertScaleAbs(self.previous_frame)) # moving_average - curframe

            self.gray_frame = cv2.cvtColor(self.absdiff_frame, cv2.COLOR_BGR2GRAY) #Convert to gray otherwise can't do threshold
            ret, self.gray_frame = cv2.threshold(self.gray_frame, 50, 255, cv2.THRESH_BINARY)

            self.gray_frame = cv2.dilate(self.gray_frame, None, iterations=15) #to get object blobs
            self.gray_frame = cv2.erode(self.gray_frame, None, iterations=10)

    def somethingHasMoved(self):
        # motionPercent = 100.0 * cv2.countNonZero(self.gray_frame) / (self.frame_width * self.frame_height)
        # print(motionPercent)
        # Find contours
        image, contours, heirarchy = cv2.findContours(self.gray_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            self.currentcontours = contours # Save contours
        for contour in contours:
            self.currentsurface += cv2.contourArea(contour)

        # Filter out inside rectangles
        avg = (self.currentsurface * 100) / self.surface #Calculate the average of contour area on the total size
        self.currentsurface = 0 #Put back the current surface to 0
        print(avg, self.threshold)
        if avg > self.threshold:
            print('moved')
            self.motionDetected = True
        else:
            # print('still')
            self.motionDetected = False

if __name__=="__main__":
    detect0 = MotionDetectorAdaptative(doRecord=True, camId=0)
    detect1 = MotionDetectorAdaptative(doRecord=True, camId=1)
    detect2 = MotionDetectorAdaptative(doRecord=True, camId=2)
    detect0.run()
    detect1.run()
    detect2.run()

