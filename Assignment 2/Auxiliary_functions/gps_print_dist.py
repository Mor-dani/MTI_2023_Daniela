#LCD
import RPi.GPIO as GPIO
#Defining the GPIO notation- Board uses the pins on board instead of the GPIO numbers
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
from RPLCD.gpio import CharLCD
lcd = CharLCD(cols=16, rows=2, pin_rs=37, pin_e=35, pins_data=[40,38,36,32],numbering_mode=GPIO.BOARD)

#GPS data
from sys import argv
import gps
import requests
#for calculating the distance to the train station
import geopy.distance
COORDS_TRAIN = (-37.844446617388767, 145.002200570393)

#listen on port 2947 of gpsd
session = gps.gps("localhost","2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)


while True :
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
            #print(lat_current_str)
            #printing on LCD
            #lcd.cursor_pos = (0,0)
            string_lcd = lat_current_str + "," + lon_current_str
            #lcd.cursor_pos = (0,0)
            #lcd.write_string(string_lcd)
            #print(string_lcd)
            string_lcd = "dist:" + dist_str + "km"
            lcd.cursor_pos = (1,0)
            lcd.write_string(string_lcd)
            
            #print(string_lcd)
            
            #lcd.write_string(string_lcd)
            
            
    except Exception as e:
        print("Got exception: " +str(e))






