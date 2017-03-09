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

# config
parser = ConfigParser.SafeConfigParser()
parser.read('config.ini')
links = parser.getint('roi_referenz', 'links')
rechts = parser.getint('roi_referenz', 'rechts')
unten = parser.getint('roi_referenz', 'unten')
oben = parser.getint('roi_referenz', 'oben')

#Trackbar
def nothing(x):
    pass

cv2.namedWindow("Frame")
cv2.createTrackbar('links', 'Frame', 0, 640, nothing)
cv2.createTrackbar('rechts', 'Frame', 0, 640, nothing)
cv2.createTrackbar('oben', 'Frame', 0, 480, nothing)
cv2.createTrackbar('unten', 'Frame', 0, 480, nothing)

#Values from before
cv2.setTrackbarPos('links', 'Frame', links)
cv2.setTrackbarPos('rechts', 'Frame', rechts)
cv2.setTrackbarPos('oben', 'Frame', oben)
cv2.setTrackbarPos('unten', 'Frame', unten)

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

#solange Kamera frames hergibt
for frame in camera.capture_continuous(rawCapture, format = "bgr", use_video_port=True):

    key = cv2.waitKey(1) & 0xFF

    links = cv2.getTrackbarPos('links','Frame')
    rechts = cv2.getTrackbarPos('rechts','Frame')
    oben = cv2.getTrackbarPos('oben','Frame')
    unten = cv2.getTrackbarPos('unten','Frame')

    #schleife bei q verlassen
    if key == ord("q"):
        parser.set('roi_referenz', 'links', str(links))
        parser.set('roi_referenz', 'rechts', str(rechts))
        parser.set('roi_referenz', 'oben', str(oben))
        parser.set('roi_referenz', 'unten', str(unten))
        parser.set('roi_referenz', 'radius', str(radius))
        parser.set('roi_referenz', 'centerArea1x', str(center1[0]))
        parser.set('roi_referenz', 'centerArea2x', str(center2[0]))
        parser.set('roi_referenz', 'centerArea3x', str(center3[0]))
        parser.set('roi_referenz', 'centerArea4x', str(center4[0]))
        parser.set('roi_referenz', 'centerArea1y', str(center1[1]))
        parser.set('roi_referenz', 'centerArea2y', str(center2[1]))
        parser.set('roi_referenz', 'centerArea3y', str(center3[1]))
        parser.set('roi_referenz', 'centerArea4y', str(center4[1]))
        with open('config.ini', 'w') as configfile:
            parser.write(configfile)
        rawCapture.truncate(0)
        break

    #bild aufnehmen
    image = frame.array

    #bild bearbeiten

    roiImage = image[oben:unten, links:rechts] # Region of Interest setzen
    cv2.rectangle(image, (links, oben), (rechts, unten), (0,0,255),3) # (x,y) (x+w,y+h) (farbe) (dicke)
    cv2.rectangle(image, (links, oben), ((rechts - (rechts - links)/2), unten), (0,0,255),3) # (x,y) (x+w,y+h) (farbe) (dicke)
    cv2.rectangle(image, (links, oben), (rechts, (unten - (unten - oben)/2)), (0,0,255),3) # (x,y) (x+w,y+h) (farbe) (dicke)
    if (rechts - links) < (unten - oben):
        radius = (rechts -links) / 4
    else:
        radius = (unten - oben) / 4
    center1 = (links + (rechts - links)/4, oben + (unten - oben)/4)
    center2 = (rechts - (rechts - links)/4, oben + (unten - oben)/4)
    center3 = (links + (rechts - links)/4, unten - (unten - oben)/4)
    center4 = (rechts - (rechts - links)/4, unten - (unten - oben)/4)
    cv2.circle(image,center1,radius,(0,255,0),2)
    cv2.circle(image,center2,radius,(0,255,0),2)
    cv2.circle(image,center3,radius,(0,255,0),2)
    cv2.circle(image,center4,radius,(0,255,0),2)

            
    #bild anzeigen
    camera.annotate_text = "Press q to quit"
    cv2.imshow("Frame", image)
    cv2.imshow("Referenzarea", roiImage)

    #aufräumen
    rawCapture.truncate(0)

