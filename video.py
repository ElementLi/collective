#!/usr/bin/python3

import numpy as np
import cv2
import time
import imutils
from imutils.video import FPS
import argparse

# to read a video file, construct the argument parse and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument('-v', '--video', required=True,
#                 help='path to input video file')
# args = vars(ap.parse_args())

# cap = cv2.VideoCapture(args['video'])
cap = cv2.VideoCapture(1)
cap.set(3, 1280)
cap.set(4, 720)
time.sleep(2)
cap.set(60, -8.0)
fps = FPS().start()

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter('output.avi', fourcc, 25.0, (1280, 720))

while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        # write the frame
        out.write(frame)
        frame = imutils.resize(frame, width=500)
        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        fps.update()
    else:
        break

# Release everything if job is finished
cap.release()
out.release()
cv2.destroyAllWindows()