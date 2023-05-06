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
            print(str(rep.lat)+","+str(rep.lon))
            lat_current = rep.lat
            lon_current = rep.lon
            coords_current =  (lat_current, lon_current)
            print(geopy.distance.distance(coords_current, COORDS_TRAIN).km)
            
    except Exception as e:
        print("Got exception: " +str(e))
