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

#default camera values
#camera.sharpness = 0
#camera.contrast = 0
#camera.brightness = 50
#camera.saturation = 0
#camera.iso = 0 # auto
#camera.exposure_mode = 'auto'
#camera.meter_mode = 'average'
#camera.awb_mode = 'auto'

rawCapture = PiRGBArray(camera, size=(640, 480))
#cap = cv2.VideoCapture(0) < so kann man auch bild aufnehmen

#kamera hochfahren lassen
time.sleep(2.5)

# socket UDP config
#UDP_IP = "127.0.0.1"
UDP_IP = "169.254.255.255"
UDP_PORT = 5005
MESSAGE = "Hello World!"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

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

    roiImage = image[bandO:bandU, bandL:bandR] # Region of Interest setzen
    cv2.rectangle(image, (bandL, bandO), (bandR, bandU), (0,0,255),3) # (x,y) (x+w,y+h) (farbe) (dicke)
    grayImage = cv2.cvtColor(roiImage, cv2.COLOR_BGR2GRAY) # zum graubild konvertieren
    mask = fgbg.apply(grayImage)# Hintergrund abziehen
    muell, mask = cv2.threshold(mask, 5, 255, cv2.THRESH_BINARY)# binarisieren
    mask = cv2.GaussianBlur(mask,(5,5),0) # noise rausfiltern
    muell, mask = cv2.threshold(mask, 3, 255, cv2.THRESH_BINARY)# binarisieren

    #Konturen + Mittelpunkt finden
    _, contours, hierarchy = cv2.findContours(mask, 1, 2)
    areas = [cv2.contourArea(c) for c in contours]
    if not areas: # falls leer abbrechen
        numberOfFounds = 0
        rawCapture.truncate(0)
        GPIO.output(LEDR, False)
        GPIO.output(LEDY, False)
        GPIO.output(LEDG, False)
        GPIO.output(LEDB, False)
        continue
    maxIndex = np.argmax(areas)
    cnt = contours[maxIndex]
    (x,y),radius = cv2.minEnclosingCircle(cnt)
    center = (int(x),int(y))
    radius = int(radius)
    if radius < 70: # falls Radius zu klein abbrechen
        numberOfFounds = 0
        cv2.imshow("Frame", image)
        rawCapture.truncate(0)
        GPIO.output(LEDR, False)
        GPIO.output(LEDY, False)
        GPIO.output(LEDG, False)
        GPIO.output(LEDB, False)
        continue
    cv2.circle(roiImage,center,radius,(0,255,0),2)
    
    numberOfFounds = numberOfFounds + 1
    if numberOfFounds < 3: # nicht genug valide Objekte hintereinander -> keine Berechnung
        cv2.imshow("Frame", image)
        rawCapture.truncate(0)
        GPIO.output(LEDR, False)
        GPIO.output(LEDY, False)
        GPIO.output(LEDG, False)
        GPIO.output(LEDB, False)
        continue

    if center[0]< 100 or center[0] > 300: # Objekt am Rand -> keine Berechnung
        cv2.imshow("Frame", image)
        rawCapture.truncate(0)
        GPIO.output(LEDR, False)
        GPIO.output(LEDY, False)
        GPIO.output(LEDG, False)
        GPIO.output(LEDB, False)
        continue

    hsvImage = cv2.cvtColor(roiImage,cv2.COLOR_BGR2HSV) # zum HSV Bild konvertieren

    # offsetkorrektur
    if center[1]-radius < 0 :
        objectImageY = 0
    else:
        objectImageY = center[1]-radius
    if center[0]-radius < 0 :
        objectImageX = 0
    else:
        objectImageX = center[0]-radius
    
    objectImage = hsvImage[objectImageY : center[1]+radius, objectImageX : center[0]+radius]
    objectImageCenter = hsvImage[objectImageY + (radius / 2)  : center[1] + (radius / 2) , objectImageX + (radius / 2): center[0] + (radius / 2)]

    #b,g,r = cv2.split(image)
    h,s,v = cv2.split(objectImageCenter)

    averageRowHue = np.average(h, axis=0) 
    averageRowSaturation = np.average(s, axis=0) 
    averageRowValue = np.average(v, axis=0) 

    averageHue = np.average(averageRowHue)
    averageSaturation = np.average(averageRowSaturation)
    averageValue = np.average(averageRowValue) 

    print averageHue
    #print averageSaturation
    #print averageValue

    HLow = cv2.getTrackbarPos('HLow','Frame')
    HHigh = cv2.getTrackbarPos('HHigh','Frame')
    SLow = cv2.getTrackbarPos('SLow','Frame')
    SHigh = cv2.getTrackbarPos('SHigh','Frame')
    VLow = cv2.getTrackbarPos('VLow','Frame')
    VHigh = cv2.getTrackbarPos('VHigh','Frame')
    
    if averageValue < 25:
        print "Bild zu dunkel"
    elif averageSaturation < 25:
        print "Bild zu hell"
    else:
        print "Bild ok"
        GPIO.output(LEDR, False)
        GPIO.output(LEDY, False)
        GPIO.output(LEDG, False)
        GPIO.output(LEDB, False)
        if (averageHue < 10) or (averageHue >= 150): #rot
            cv2.putText(image, "RED", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255),2,cv2.LINE_AA)
            GPIO.output(LEDR, True)
        elif averageHue >= 10 and averageHue < 40: #gelb
            cv2.putText(image, "YELLOW", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255),2,cv2.LINE_AA)
            GPIO.output(LEDY, True)
        elif averageHue >= 40 and averageHue < 85: #grün
            cv2.putText(image, "GREEN", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255),2,cv2.LINE_AA)
            GPIO.output(LEDG, True)
        elif averageHue >= 85 and averageHue < 150: #blau
            cv2.putText(image, "BLUE", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255),2,cv2.LINE_AA)
            GPIO.output(LEDB, True)
        else:
            print "irgendwie schiefgelaufen..."
            
    
    #bild anzeigen
    camera.annotate_text = "Press q to quit"
    cv2.imshow("Frame", image)
    #cv2.imshow("mask",  mask)
    cv2.imshow("objectImage", objectImageCenter)
    #cv2.imshow("roiImage", roiImage)

    print "Sende Daten"
    try:
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    except:
        print "could not send Data, please check Connection"
    
    #aufräumen
    rawCapture.truncate(0)

