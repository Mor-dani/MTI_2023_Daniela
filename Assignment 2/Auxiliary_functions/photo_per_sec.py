import cv2
import time

num = 1
cap = cv2.VideoCapture(0)

while True:
    ret, img = cap.read()
    cv2.imshow('Frame', img)
    time.sleep(2)
    #if cv2.waitKey(1) & 0xFF == ord('
    cv2.imwrite('/home/pi/images/test_3_'+str(num)+'.jpg',img)
    print('Capture '+str(num)+ ' Successful')
    num=num+1
        
    if num==4:
        break
    time.sleep(1)
        

cap.release()
cv2.detroyAllWindows()