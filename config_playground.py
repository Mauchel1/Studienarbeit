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
import ConfigParser

#setup

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

LEDR = 4
LEDY = 27
LEDG = 17
LEDB = 22

GPIO.setup(LEDR, GPIO.OUT, initial = 0)
GPIO.setup(LEDY, GPIO.OUT, initial = 0)
GPIO.setup(LEDG, GPIO.OUT, initial = 0)
GPIO.setup(LEDB, GPIO.OUT, initial = 0)

fgbg = cv2.createBackgroundSubtractorMOG2(5000, 50)
#fgbg = cv2.createBackgroundSubtractorMOG2()
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
parser.read('/home/pi/Studienarbeit/config.ini')
bandL = parser.getint('roi_band', 'links')
bandR = parser.getint('roi_band', 'rechts')
bandU = parser.getint('roi_band', 'unten')
bandO = parser.getint('roi_band', 'oben')

# wird nur ausgeführt bei aufruf mit "python -O XXX"
if not __debug__:
    print "CONFIG MODE"

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

    roiImage = image # Region of Interest setzen
    cv2.rectangle(image, (bandL, bandO), (bandR, bandU), (0,0,255),3) # (x,y) (x+w,y+h) (farbe) (dicke)
    grayImage = cv2.cvtColor(roiImage, cv2.COLOR_BGR2GRAY) # zum graubild konvertieren
    mask = fgbg.apply(grayImage)# Hintergrund abziehen
    muell, mask = cv2.threshold(mask, 5, 255, cv2.THRESH_BINARY)# binarisieren
    mask = cv2.GaussianBlur(mask,(5,5),0) # noise rausfiltern
    muell, mask = cv2.threshold(mask, 3, 255, cv2.THRESH_BINARY)# binarisieren
    
    #bild anzeigen
    camera.annotate_text = "Press q to quit"
    cv2.imshow("Frame", image)
    cv2.imshow("mask",  mask)
    #cv2.imshow("roiImage", roiImage)
    
    #aufräumen
    rawCapture.truncate(0)

