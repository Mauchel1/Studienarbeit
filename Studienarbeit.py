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

hue = RED / 2
lower_range = np.array([max(0,hue-20),0,0], dtype=np.uint8)
upper_range = np.array([min(180,hue+20),255,255], dtype=np.uint8)

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
    grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # zum graubild konvertieren
    cv2.rectangle(image, (100, 150), (530, 350), (0,0,255),3) # (x,y) (x+w,y+h) (farbe) (dicke)
    roiImage = image[150:350, 100:530] # Region of Interest setzen
    hsvImage = cv2.cvtColor(roiImage,cv2.COLOR_BGR2HSV) # zum HSV Bild konvertieren
    mask = cv2.inRange(hsvImage, lower_range, upper_range) # threshold für blauen kanal

    #b,g,r = cv2.split(image)
    h,s,v = cv2.split(hsvImage)

    averageHue = 0 #TODO
    averageSaturation = 0 #TODO
    averageValue = 0 #TODO

    i = 0
    for column in xrange (0, np.size(hsvImage, 1)-1): # TODO optimieren - dauert LANGE
        for row in xrange (0, np.size(hsvImage, 0)-1):
            averageHue += hsvImage[row][column][0]
            averageSaturation += hsvImage[row][column][1]
            averageValue += hsvImage[row][column][2]

    averageValue /= np.size(hsvImage, 1) * np.size(hsvImage, 0)
    averageSaturation /= np.size(hsvImage, 1) * np.size(hsvImage, 0)
    averageHue /= np.size(hsvImage, 1) * np.size(hsvImage, 0)

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
    cv2.imshow("Frame", h)
    #cv2.imshow("mask", mask)
    #cv2.imshow("roiImage", roiImage)
    key = cv2.waitKey(1) & 0xFF

    #aufräumen
    rawCapture.truncate(0)

    #schleife bei q verlassen
    if key == ord("q"):
        break

