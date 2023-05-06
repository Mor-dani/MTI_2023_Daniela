from sys import argv
import gps
import requests

#listen on port 2947 of gpsd
session = gps.gps("localhost","2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

while True :
    rep=session.next()
    try:
        if(rep["class"]=="TPV"):
            print(str(rep.lat)+","+str(rep.lon))
            
    except Exception as e:
        print("Got exception: " +str(e))