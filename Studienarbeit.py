# -*- coding: utf-8 -*-
# import packages

from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np

#variablen anlegen
YELLOW = 30
BLUE = 210
GREEN = 145
RED = 320

fgbg = cv2.createBackgroundSubtractorMOG2()

#kamera init
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 42 #max 40-90
camera.iso = 400

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

#solange Kamera frames hergibt
for frame in camera.capture_continuous(rawCapture, format = "bgr", use_video_port=True):

    #bild aufnehmen
    #camera.capture(rawCapture, format="bgr")
    image = frame.array

    #bild bearbeiten

    roiImage = image[150:350, 100:530] # Region of Interest setzen
    cv2.rectangle(image, (100, 150), (530, 350), (0,0,255),3) # (x,y) (x+w,y+h) (farbe) (dicke)
    grayImage = cv2.cvtColor(roiImage, cv2.COLOR_BGR2GRAY) # zum graubild konvertieren
    mask = fgbg.apply(grayImage)# Hintergrund abziehen
    muell, mask = cv2.threshold(mask, 5, 255, cv2.THRESH_BINARY)# binarisieren
    mask = cv2.GaussianBlur(mask,(5,5),0) # noise rausfiltern
    muell, mask = cv2.threshold(mask, 3, 255, cv2.THRESH_BINARY)# binarisieren

    #Konturen + Mittelpunkt finden
    _, contours, hierarchy = cv2.findContours(mask, 1, 2)
    areas = [cv2.contourArea(c) for c in contours]
    if not areas: # falls leer abbrechen
        rawCapture.truncate(0)
        continue
    maxIndex = np.argmax(areas)
    cnt = contours[maxIndex]
    (x,y),radius = cv2.minEnclosingCircle(cnt)
    center = (int(x),int(y))
    radius = int(radius)
    if radius < 12: # falls Radius zu klein abbrechen
        rawCapture.truncate(0)
        continue
    cv2.circle(roiImage,center,radius,(0,255,0),2)
    
    hsvImage = cv2.cvtColor(roiImage,cv2.COLOR_BGR2HSV) # zum HSV Bild konvertieren

    if center[1]-radius < 0 :
        objectImageY = 0
    else:
        objectImageY = center[1]-radius
    if center[0]-radius < 0 :
        objectImageX = 0
    else:
        objectImageX = center[0]-radius
    
    objectImage = hsvImage[objectImageY : center[1]+radius, objectImageX : center[0]+radius] 

    #b,g,r = cv2.split(image)
    h,s,v = cv2.split(objectImage)

    averageRowHue = np.average(h, axis=0) 
    averageRowSaturation = np.average(s, axis=0) 
    averageRowValue = np.average(v, axis=0) 

    averageHue = np.average(averageRowHue)
    averageSaturation = np.average(averageRowSaturation)
    averageValue = np.average(averageRowValue) 

    print averageHue
    print averageSaturation
    print averageValue
    
    if averageValue < 25:
        print "Bild zu dunkel"
    elif averageSaturation < 25:
        print "Bild zu hell"
    else:
        print "Bild ok"
        if (averageHue < 20) or (averageHue >= 150): #rot
            print "rot"
        elif averageHue >= 20 and averageHue < 40: #gelb
            print "gelb"            
        elif averageHue >= 40 and averageHue < 85: #grün
            print "grün"
        elif averageHue >= 85 and averageHue < 150: #blau
            print "blau"
        else:
            print "irgendwie schiefgelaufen..."
            
    
    #bild anzeigen
    camera.annotate_text = "Press q to quit"
    cv2.imshow("Frame", image)
    #cv2.imshow("mask",  mask)
    #cv2.imshow("objectImage", objectImage)
    #cv2.imshow("roiImage", roiImage)
    key = cv2.waitKey(1) & 0xFF

    #aufräumen
    rawCapture.truncate(0)

    #schleife bei q verlassen
    if key == ord("q"):
        break

