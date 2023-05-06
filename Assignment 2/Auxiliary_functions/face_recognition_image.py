import numpy as np
import cv2

#image = cv2.imread('image2.jpg')
#start using camera
cap = cv2.VideoCapture(0)

#importing classifiers
face_cascade= cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

def detect_face(img_gray, img_colour):
    '''
    #sending picture to the classifier, return will be coordinates of the face
    face = face_cascade.detectMultiScale(img_gray)
    #assigning the coordinates to x,y,w,h
    for (x,y,w,h) in face:
        #drawing a rectange around these points
        cv2.rectangle(img_colour,(x,y),(x+w,y+h),(255,0,0),5)
        #creating a region of interest to look for eyes only in faces
        roi_gray = img_gray[y:y+h, :+x+w]
        roi_colour = img_colour[y:y+h, x:x+w]
    '''
    #analyse the faces for eyes
        #adding a restriction for the smaller and bigger sizes
    eyes = eye_cascade.detectMultiScale(img_gray, minNeighbors=6) 
    #analysing only in the region of interest led to worse results and often finding eyes outside of the face
    #eyes = eye_cascade.detectMultiScale(roi_colour)
    #will need to create a vector for storing eyes for then analysing if they are open or not
    for (x,y,w,h) in eyes:
        #drawing a rectange around these points
        cv2.rectangle(img_colour,(x,y),(x+w,y+h),(0,0,255),1)
        #creating a region of interest to look for eyes only in faces
        #roi_gray = img_gray[y:y+h, :+x+w]
        #roi_colour = img_colour[y:y+h, x:x+w]
     
    eyes = eye_cascade.detectMultiScale(img_gray, minNeighbors=6, minSize = (70,70)) 
    #analysing only in the region of interest led to worse results and often finding eyes outside of the face
    #will need to create a vector for storing eyes for then analysing if they are open or not
    for (x,y,w,h) in eyes:
        #drawing a rectange around these points
        cv2.rectangle(img_colour,(x,y),(x+w,y+h),(0,255,0),5)
        
    return img_colour

#taking photos
while 1:
    #take photo
    ret, image_colour = cap.read()
    #black and white image
    image = cv2.cvtColor(image_colour, cv2.COLOR_BGR2GRAY)
    #show the image
    #cv2.imshow('Frame', image)
    image_marked = detect_face(image, image_colour)

    #show the image with the rectangle
    cv2.imshow('Preview',image_marked)
    #Close when keyboard pressed
    k = cv2.waitKey(30) & 0xff
    if k==27:
        break
cap.release()
cv2.destroyAllWindows()


'''
x = coord[0][0]
y = coord[0][1]
w = coord[0][2]
h = coord[0][3]
'''


#print(coord)
