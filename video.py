#!/usr/bin/python3

import sys
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
parser = argparse.ArgumentParser(
    description='Perform ' + sys.argv[0] + ' example operation on incoming camera/video image')
parser.add_argument('-c', '--camera_to_use', type=int, help='specify camera to use', default=0)
args = parser.parse_args()

# cam = cv2.VideoCapture(args['video'])
cam = cv2.VideoCapture(args.camera_to_use)
cam.set(3, 1280)
cam.set(4, 720)
time.sleep(2)
cam.set(60, -8.0)
fps = FPS().start()

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter('output.avi', fourcc, 25.0, (1280, 720))

try:
    K = np.load('camera_config/k' + str(args.camera_to_use) + '.npy')
except:
    print('No undistort matrix found.')

try:
    D = np.load('camera_config/d' + str(args.camera_to_use) + '.npy')
except:
    print('No undistort distance found.')

while cam.isOpened():
    cam.grab()
    ret, frame = cam.read()
    if ret:
        if 'K' not in vars() or 'K' not in globals() or 'D' not in vars() or 'D' not in globals():
            out.write(frame)
            frame = imutils.resize(frame, width=800)
            cv2.imshow('frame', frame)
        else:
            undistort = cv2.undistort(frame, K, D)
            # write the undistort frame
            out.write(undistort)
            undistort = imutils.resize(undistort, width=800)
            cv2.imshow('undistort', undistort)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        fps.update()
    else:
        break

# Release everything if job is finished
cam.release()
out.release()
cv2.destroyAllWindows()
