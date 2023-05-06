# import the necessary packages
from imutils.video import VideoStream
from imutils import face_utils
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2


#GPS data
from sys import argv
import gps
import requests
#for calculating the distance to the train station
import geopy.distance
COORDS_TRAIN = (-37.844446617388767, 145.002200570393)
#Distance under which the system must alert the user if they are asleep
THRESHOLD_DISTANCE = 0.4
close_to_station = False

#H bridge - controlling the motor
import RPi.GPIO as GPIO
#Defining the GPIO notation- Board uses the pins on board instead of the GPIO numbers
GPIO.setmode(GPIO.BOARD)
#Defining our outputs
ENABLE_PIN = 40
DRIVER_PIN1 = 36
DRIVER_PIN2 = 38
GPIO.setup(ENABLE_PIN, GPIO.OUT)
GPIO.setup(DRIVER_PIN1, GPIO.OUT)
GPIO.setup(DRIVER_PIN2, GPIO.OUT)


def euclidean_dist(ptA, ptB):
	# compute and return the euclidean distance between the two
	# points
	return np.linalg.norm(ptA - ptB)

def eye_aspect_ratio(eye):
	# compute the euclidean distances between the two sets of
	# vertical eye landmarks (x, y)-coordinates
	A = euclidean_dist(eye[1], eye[5])
	B = euclidean_dist(eye[2], eye[4])
	# compute the euclidean distance between the horizontal
	# eye landmark (x, y)-coordinates
	C = euclidean_dist(eye[0], eye[3])
	# compute the eye aspect ratio
	ear = (A + B) / (2.0 * C)
	# return the eye aspect ratio
	return ear


# define two constants, one for the eye aspect ratio to indicate
# blink and then a second constant for the number of consecutive
# frames the eye must be below the threshold for to set off the
# alarm
EYE_AR_THRESH = 0.2
EYE_AR_CONSEC_FRAMES = 4
# initialize the frame counter as well as a boolean used to
# indicate if the alarm is going off
COUNTER = 0
ALARM_ON = False

# load OpenCV's Haar cascade for face detection (which is faster than
# dlib's built-in HOG detector, but less accurate), then create the
# facial landmark predictor
print("[INFO] loading facial landmark predictor...")
detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# grab the indexes of the facial landmarks for the left and
# right eye, respectively
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

#Starting the GPS
#listen on port 2947 of gpsd
session = gps.gps("localhost","2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
string_distance = ""

#start using camera
cap = cv2.VideoCapture(0)
#make sure everything in the motor is turned off
GPIO.output(ENABLE_PIN , False)
GPIO.output(DRIVER_PIN1, False)
GPIO.output(DRIVER_PIN2, False)

#let the camera warm up
time.sleep(2)


# loop over frames from the video stream
while True:
    #Get current coordinates of GPS
    rep=session.next()
    try:
        if(rep["class"]=="TPV"):
            #print(str(rep.lat)+","+str(rep.lon))
            lat_current = rep.lat
            lon_current = rep.lon
            coords_current =  (lat_current, lon_current)
            distance_to_station = geopy.distance.distance(coords_current, COORDS_TRAIN).km
            #print(type(lat_current))
            lat_current_str = "{:.2f}".format(lat_current)
            lon_current_str = "{:.2f}".format(lon_current)
            dist_str ="{:.3f}".format(distance_to_station)
            
            if THRESHOLD_DISTANCE > distance_to_station:
                #User is within the threshold to wake up!
                string_distance = "dist:" + dist_str + "km. ALERT!"
                close_to_station = True
            else:
                string_distance = "dist:" + dist_str + "km"
                close_to_station = False
            
            
            
            
            #Drowsiness detection in the current frame:
            
            # grab the frame from the threaded video file stream, resize
            # it, and convert it to grayscale
            # channels)
            ret, frame = cap.read()
            frame = imutils.resize(frame, width=450)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # detect faces in the grayscale frame
            rects = detector.detectMultiScale(gray, scaleFactor=1.1, 
                minNeighbors=5, minSize=(40, 40),
                flags=cv2.CASCADE_SCALE_IMAGE)
            #change the factors later to optimise to my own
            
            # loop over the face detections
            for (x, y, w, h) in rects:
                # construct a dlib rectangle object from the Haar cascade
                # bounding box
                rect = dlib.rectangle(int(x), int(y), int(x + w),
                    int(y + h))
                # determine the facial landmarks for the face region, then
                # convert the facial landmark (x, y)-coordinates to a NumPy
                # array
                shape = predictor(gray, rect)
                shape = face_utils.shape_to_np(shape)
                # extract the left and right eye coordinates, then use the
                # coordinates to compute the eye aspect ratio for both eyes
                leftEye = shape[lStart:lEnd]
                rightEye = shape[rStart:rEnd]
                leftEAR = eye_aspect_ratio(leftEye)
                rightEAR = eye_aspect_ratio(rightEye)
                # average the eye aspect ratio together for both eyes
                ear = (leftEAR + rightEAR) / 2.0
                # compute the convex hull for the left and right eye, then
                # visualize each of the eyes
                leftEyeHull = cv2.convexHull(leftEye)
                rightEyeHull = cv2.convexHull(rightEye)
                cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
                cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
                # check to see if the eye aspect ratio is below the blink
                # threshold, and if so, increment the blink frame counter
                if ear < EYE_AR_THRESH:
                    COUNTER += 1
                    # if the eyes were closed for a sufficient number of
                    # frames, AND user is close to the station, then sound the alarm
                    if (COUNTER >= EYE_AR_CONSEC_FRAMES) and (close_to_station):
                        # if the alarm is not on, turn it on
                        if not ALARM_ON:
                            ALARM_ON = True
                            # check to see if the TrafficHat buzzer should
                            # be sounded
                            """
                            if args["alarm"] > 0:
                                th.buzzer.blink(0.1, 0.1, 10,
                                    background=True)
                                    """
                        # draw an alarm on the frame
                        cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        
                        #Turn on the motor for the alarm
                        GPIO.output(ENABLE_PIN , True)
                        GPIO.output(DRIVER_PIN1, False)
                        GPIO.output(DRIVER_PIN2, True)
                # otherwise, the eye aspect ratio is not below the blink
                # threshold, so reset the counter and alarm
                else:
                    COUNTER = 0
                    ALARM_ON = False
                    GPIO.output(ENABLE_PIN , False)
                    GPIO.output(DRIVER_PIN1, False)
                    GPIO.output(DRIVER_PIN2, False)
                # draw the computed eye aspect ratio on the frame to help
                # with debugging and setting the correct eye aspect ratio
                # thresholds and frame counters
                cv2.putText(frame, "EAR: {:.3f}".format(ear), (300, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                #Add the current distance to the train station
                cv2.putText(frame, string_distance, (30, 300),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 0), 2)
         
            # show the frame
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF
         
            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break

            
            
            
    except Exception as e:
        print("Got exception: " +str(e))
# do a bit of cleanup
cap.release()
cv2.destroyAllWindows()
GPIO.cleanup()



