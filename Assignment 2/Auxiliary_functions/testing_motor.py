#Importing the libraries
from time import sleep
import RPi.GPIO as GPIO
#Defining the GPIO notation- Board uses the pins on board instead of the GPIO numbers
GPIO.setmode(GPIO.BOARD)
#Defining our outputs
ENABLE_PIN = 40
GPIO.setup(ENABLE_PIN, GPIO.OUT)



#Enable pin
GPIO.output(ENABLE_PIN , GPIO.HIGH)
#Need h-bridge

#sleep(3)
#GPIO.output(ENABLE_PIN , False)


sleep(3)
GPIO.output(ENABLE_PIN , GPIO.LOW)

GPIO.cleanup()