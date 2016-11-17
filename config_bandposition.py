#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import packages

from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import io
import ConfigParser

#Trackbar
def nothing(x):
    pass

cv2.namedWindow("Frame")
cv2.createTrackbar('links', 'Frame', 0, 640, nothing)
cv2.createTrackbar('rechts', 'Frame', 0, 640, nothing)
cv2.createTrackbar('oben', 'Frame', 0, 480, nothing)
cv2.createTrackbar('unten', 'Frame', 0, 480, nothing)

#standard Values
cv2.setTrackbarPos('links', 'Frame', 100)
cv2.setTrackbarPos('rechts', 'Frame', 530)
cv2.setTrackbarPos('oben', 'Frame', 150)
cv2.setTrackbarPos('unten', 'Frame', 350)

#kamera init
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 42 #max 40-90
camera.iso = 1200

time.sleep(2)
camera.shutter_speed = camera.exposure_speed
camera.exposure_mode = 'off'
g = camera.awb_gains
camera.awb_mode = 'off'
camera.awb_gains = g

rawCapture = PiRGBArray(camera, size=(640, 480))
#cap = cv2.VideoCapture(0) < so kann man auch bild aufnehmen

#kamera hochfahren lassen
time.sleep(2.5)

# config
parser = ConfigParser.SafeConfigParser()
parser.read('config.ini')

#solange Kamera frames hergibt
for frame in camera.capture_continuous(rawCapture, format = "bgr", use_video_port=True):

    key = cv2.waitKey(1) & 0xFF

    links = cv2.getTrackbarPos('links','Frame')
    rechts = cv2.getTrackbarPos('rechts','Frame')
    oben = cv2.getTrackbarPos('oben','Frame')
    unten = cv2.getTrackbarPos('unten','Frame')

    #schleife bei q verlassen
    if key == ord("q"):
        parser.set('roi_band', 'links', str(links))
        parser.set('roi_band', 'rechts', str(rechts))
        parser.set('roi_band', 'oben', str(oben))
        parser.set('roi_band', 'unten', str(unten))
        with open('config.ini', 'w') as configfile:
            parser.write(configfile)
        rawCapture.truncate(0)
        break

    #bild aufnehmen
    image = frame.array

    #bild bearbeiten

    roiImage = image[oben:unten, links:rechts] # Region of Interest setzen
    cv2.rectangle(image, (links, oben), (rechts, unten), (0,0,255),3) # (x,y) (x+w,y+h) (farbe) (dicke)
            
    #bild anzeigen
    camera.annotate_text = "Press q to quit"
    cv2.imshow("Frame", image)
    cv2.imshow("Laufband", roiImage)

    #aufräumen
    rawCapture.truncate(0)

