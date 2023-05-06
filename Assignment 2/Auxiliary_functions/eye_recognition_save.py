import numpy as np
import cv2

#image = cv2.imread('image2.jpg')
#start using camera
cap = cv2.VideoCapture(0)
num = 1
#importing classifiers
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
"""
def eye_status(eye):
    #function for evaluating the possibility of an eye being open or not
    break
  """  

def detect_eyes(img_gray, img_colour):

    global num
    #analyse for eyes
    
     
    eyes = eye_cascade.detectMultiScale(img_gray, minNeighbors=10, minSize = (90,90)) 
    #analysing only in the region of interest led to worse results and often finding eyes outside of the face
    #will need to create a vector for storing eyes for then analysing if they are open or not
    print(eyes)
    for coord in eyes:
        print(coord)
        #print(eye)
        #take each eye and analyse if it is open or not
        x = coord[0]
        y = coord[1]
        w = coord[2]
        h = coord[3]
        #cropping the eye
        eye = img_gray[y:y+h, x:x+w]
        cv2.imshow('Eye',eye)
        #save the image
        cv2.imwrite('/home/pi/Desktop/MTI/A2/eyes/eye2_'+str(num)+'.jpg',eye)
        
        num += 1
        
        
        
    for (x,y,w,h) in eyes:
        #drawing a rectange around these points
        cv2.rectangle(img_colour,(x,y),(x+w,y+h),(0,255,0),5)
        #creating a region of interest to look for eyes only in faces
        #roi_gray = img_gray[y:y+h, :+x+w]
        #roi_colour = img_colour[y:y+h, x:x+w]
        
    return img_colour

#taking photos
while 1:
    #take photo
    ret, image_colour = cap.read()
    #black and white image
    image = cv2.cvtColor(image_colour, cv2.COLOR_BGR2GRAY)
    #show the image
    #cv2.imshow('Frame', image)
    image_marked = detect_eyes(image, image_colour)

    #show the image with the rectangle
    cv2.imshow('Preview',image_marked)
    #Close when keyboard pressed
    k = cv2.waitKey(60) & 0xff
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


