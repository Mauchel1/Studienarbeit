#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import packages

from picamera.array import PiRGBArray
from picamera import PiCamera
import RPi.GPIO as GPIO
import time
import cv2
import numpy as np
import io
import socket
import ConfigParser

#setup

fgbg = cv2.createBackgroundSubtractorMOG2()
numberOfFounds = 0

#Trackbar
def nothing(x):
    pass

cv2.namedWindow("Frame")
cv2.createTrackbar('HLow', 'Frame', 0, 180, nothing)
cv2.createTrackbar('HHigh', 'Frame', 0, 180, nothing)
cv2.createTrackbar('SLow', 'Frame', 0, 255, nothing)
cv2.createTrackbar('SHigh', 'Frame', 0, 255, nothing)
cv2.createTrackbar('VLow', 'Frame', 0, 255, nothing)
cv2.createTrackbar('VHigh', 'Frame', 0, 255, nothing)
cv2.setTrackbarPos('HHigh', 'Frame', 180)
cv2.setTrackbarPos('SHigh', 'Frame', 255)
cv2.setTrackbarPos('VHigh', 'Frame', 255)

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

#kamera hochfahren lassen
time.sleep(2.5)

# config
parser = ConfigParser.SafeConfigParser()
parser.read('/home/pi/Studienarbeit/config.ini')
bandL = parser.getint('roi_band', 'links')
bandR = parser.getint('roi_band', 'rechts')
bandU = parser.getint('roi_band', 'unten')
bandO = parser.getint('roi_band', 'oben')

#solange Kamera frames hergibt
for frame in camera.capture_continuous(rawCapture, format = "bgr", use_video_port=True):

    key = cv2.waitKey(1) & 0xFF

    #schleife bei q verlassen
    if key == ord("q"):
        break

    #bild aufnehmen
    #camera.capture(rawCapture, format="bgr")
    image = frame.array

    #bild bearbeiten

    grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # zum graubild konvertieren

    hsvImage = cv2.cvtColor(image,cv2.COLOR_BGR2HSV) # zum HSV Bild konvertieren

    h,s,v = cv2.split(hsvImage)

    averageRowHue = np.average(h, axis=0) 
    averageRowSaturation = np.average(s, axis=0) 
    averageRowValue = np.average(v, axis=0) 

    averageHue = np.average(averageRowHue)
    averageSaturation = np.average(averageRowSaturation)
    averageValue = np.average(averageRowValue) 

    print averageHue
    print averageSaturation
    print averageValue

    HLow = cv2.getTrackbarPos('HLow','Frame')
    HHigh = cv2.getTrackbarPos('HHigh','Frame')
    SLow = cv2.getTrackbarPos('SLow','Frame')
    SHigh = cv2.getTrackbarPos('SHigh','Frame')
    VLow = cv2.getTrackbarPos('VLow','Frame')
    VHigh = cv2.getTrackbarPos('VHigh','Frame')

    lowColor = np.array([HLow, SLow, VLow])
    highColor = np.array([HHigh, SHigh, VHigh])

    mask = cv2.inRange(hsvImage, lowColor, highColor)

    result = cv2.bitwise_and(image, image, mask = mask)
    muell, resultthr = cv2.threshold(result, 1, 255, cv2.THRESH_BINARY)
    resultthr = cv2.cvtColor(resultthr, cv2.COLOR_BGR2GRAY)
    muell, resultthr = cv2.threshold(resultthr, 1, 255, cv2.THRESH_BINARY)
    
    if averageValue < 25:
        print "Bild zu dunkel"
    elif averageSaturation < 25:
        print "Bild zu hell"
    else:
        print "Bild ok"
        if (averageHue < 10) or (averageHue >= 150): #rot
            cv2.putText(image, "RED", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255),2,cv2.LINE_AA)
        elif averageHue >= 10 and averageHue < 40: #gelb
            cv2.putText(image, "YELLOW", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255),2,cv2.LINE_AA)
        elif averageHue >= 40 and averageHue < 85: #grün
            cv2.putText(image, "GREEN", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255),2,cv2.LINE_AA)
        elif averageHue >= 85 and averageHue < 150: #blau
            cv2.putText(image, "BLUE", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255),2,cv2.LINE_AA)
        else:
            print "irgendwie schiefgelaufen..."
            
    #bild anzeigen
    camera.annotate_text = "Press q to quit"
    cv2.imshow("Frame", image)
    cv2.imshow("result",  result)
    cv2.imshow("resultthr",  resultthr)
    
    #aufräumen
    rawCapture.truncate(0)

