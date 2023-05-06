import RPi.GPIO as GPIO
#Defining the GPIO notation- Board uses the pins on board instead of the GPIO numbers
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
from RPLCD.gpio import CharLCD



lcd = CharLCD(cols=16, rows=2, pin_rs=37, pin_e=35, pins_data=[40,38,36,32],numbering_mode=GPIO.BOARD)
lcd.write_string(u'Hello world!')