#Importing the libraries
from time import sleep
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
#Variables
OPEN_TIME = 3
CLOSING_TIME = 3
WAIT_TIME = 2


#Spin in other direction
GPIO.output(ENABLE_PIN , True)
GPIO.output(DRIVER_PIN1, False)
GPIO.output(DRIVER_PIN2, True)
sleep(CLOSING_TIME)
#Turn system off
GPIO.output(ENABLE_PIN , False)
GPIO.output(DRIVER_PIN1, False)
GPIO.output(DRIVER_PIN2, False)


GPIO.cleanup()
