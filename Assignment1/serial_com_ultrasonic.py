import time
from time import sleep
import serial
import RPi.GPIO as GPIO

#Defining the serial port
ser=serial.Serial(
    port='/dev/ttyS0',
    baudrate = 115200,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS,
    timeout = 1
    
)
#Make sure that the Pi is connected to the LTE board, otherwise it will trigger an error

#Defining the GPIO notation- Board uses the pins on board instead of the GPIO numbers
GPIO.setmode(GPIO.BOARD)
#Defining our outputs
ENABLE_PIN = 40
DRIVER_PIN1 = 36
DRIVER_PIN2 = 38
#Pins for the Ultrasonic sensor
TRIGGER_PIN = 18
ECHO_PIN = 16
#Pin configuration
GPIO.setup(ENABLE_PIN, GPIO.OUT)
GPIO.setup(DRIVER_PIN1, GPIO.OUT)
GPIO.setup(DRIVER_PIN2, GPIO.OUT)
GPIO.setup(TRIGGER_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

#Variables
DRAINING_POSITION_TIME = 2
FILLING_POSITION_TIME = 1
CLOSED_POSITION_TIME = 3
#WAIT_TIME = 5
VOLTAGE_THRESHOLD_CLEANING= 2.0
VOLTAGE_THRESHOLD_EMPTYING= 1.5
SENSOR_HEIGHT= 100 #cm

def getVoltage():
    #Request data from the lte module (about the voltage on the ldr)
    ser.write(b'1')
    print("Sent Data")
    sleep(1)
    #Read the data from the lte module (voltage on the light sensor)
    light_voltage_byte=ser.readline()
    print("Voltage byte: ",light_voltage_byte)
    #Convert to string
    light_voltage_string=light_voltage_byte.decode("utf-8")
    #Convert to float
    light_voltage=float(light_voltage_string)
    return(light_voltage)

def sendTime(code):
    #Send text messages through the lte module
    #pond finished draining
    if(code==2): 
        ser.write(b'2')
    #Pond finished filling    
    elif(code==3): 
        ser.write(b'3')
    print("Sent Code")
    sleep(2)

    return

def valveToDrainingPosition():
    #First ensure that the driver pins are low
    GPIO.output(DRIVER_PIN1, False)
    GPIO.output(DRIVER_PIN2, False)
    sleep(1)
    #Enable pin
    GPIO.output(ENABLE_PIN , True)
    #First spin in one direction for X seconds
    GPIO.output(DRIVER_PIN1, True)
    GPIO.output(DRIVER_PIN2, False)
    sleep(DRAINING_POSITION_TIME)
    #Turn off while emptying
    GPIO.output(DRIVER_PIN1, False)
    GPIO.output(DRIVER_PIN2, False)
    return

def valveToFillingPosition():
    #First ensure that the driver pins are low
    GPIO.output(DRIVER_PIN1, False)
    GPIO.output(DRIVER_PIN2, False)
    sleep(1)
    #Spin in other direction
    GPIO.output(DRIVER_PIN1, False)
    GPIO.output(DRIVER_PIN2, True)
    sleep(FILLING_POSITION_TIME)
    #Turn off while filling
    GPIO.output(DRIVER_PIN1, False)
    GPIO.output(DRIVER_PIN2, False)
    return
    
def valveToClosedPosition():
    #First ensure that the driver pins are low
    GPIO.output(DRIVER_PIN1, False)
    GPIO.output(DRIVER_PIN2, False)
    sleep(1)
    #Spin in other direction
    GPIO.output(DRIVER_PIN1, False)
    GPIO.output(DRIVER_PIN2, True)
    sleep(CLOSED_POSITION_TIME)
    #Turn off while filling
    GPIO.output(DRIVER_PIN1, False)
    GPIO.output(DRIVER_PIN2, False)
    return
    
def distance():
    
    #Ensure that we are getting reasonable values
    distance=2000.332218170166016
    while(distance>200):
        #Trigger to high
        GPIO.output(TRIGGER_PIN,True)
        #Set to low after 10 microseconds
        sleep(0.00001)
        GPIO.output(TRIGGER_PIN,False)
    
        start_time = time.time()
        stop_time = time.time()
    
        while(GPIO.input(ECHO_PIN)==0):
            start_time = time.time()
        
        while(GPIO.input(ECHO_PIN)==1):
            stop_time = time.time()
    
        #time difference
        time_passed = stop_time - start_time
        #this time is how long it took for sound to go and come back (2 times the distance)
        #2x=v*t, v is the speed of sound
        distance = (time_passed)*34300/2 #in cm
        print("distance to water: ", distance)
    return(distance)

while True:
    light_voltage=getVoltage()
    print(light_voltage)
    #Evaluate if greater than the threshold,
    if(light_voltage>VOLTAGE_THRESHOLD_CLEANING):
        #Water is too dark, need to clean!
        #First move valve to draining position
        valveToDrainingPosition()
        #Empty until light shines on sensor
        empty_yet=False
        #start_draining_time = time.time()
        #stop_draining_time = time.time() #initialising this one outside so that it isn't erased after leaving the loop
        while not(empty_yet):
            #if not empty, check the sensor until empty
            #Ultrasonic sensor to calculate the distance from the water
            distance_water=distance()
            print("Distance to water: ", distance_water)
            #Once we know the height of the sensor with respect to the bottom of the pond, we can implement the following
            height_water= SENSOR_HEIGHT - distance_water
            if(height_water<0):
                height_water=0
            
            if(height_water<20):
                #Cleaned until empty
                empty_yet=True
                #stop_draining_time = time.time()
            sleep(1)
        
        #Send notification for time it took to drain
        #draining_time= stop_draining_time - start_draining_time
        #print("draining_time: ",draining_time)
        #print("draining_time_type: ",type(draining_time))
        sendTime(2)
        
               
        #Finished draining pond, move valve to fill with clean water
        valveToFillingPosition()
        #Fill until regular height
        full_yet=False
        while not(full_yet):
            #is the code even entering this loop?
            print("Entered loop to check if full")
            #if not full, check the sensor until full
            distance_water=distance()
            height_water= SENSOR_HEIGHT - distance_water
            if(height_water<0):
                height_water=0
            #also do a sanity check to verify that noise doesn't trigger this
            if((height_water>40) and (height_water<200)):
                full_yet=True
            sleep(1)
        #Send notification for filled pond
        sendTime(3)
        #Move valve to closed position
        valveToClosedPosition()
        
    
    sleep(5)
    #Send command for measuring light




