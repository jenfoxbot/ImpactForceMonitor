#############################################
#
#Helmet Guardian: Impact Force Monitor
#
#############################################
# Code by jenfoxbot <jenfoxbot@gmail.com>
# Code is open-source, coffee/beerware
# Please keep header :)
# If you like the content, consider
#    buying me a coffee/beer or
#    contributing to my patreon (jenfoxbot)
#    to support projects like this! :D
#############################################
#
# SO MANY THANKS to the wonderful folks who
#    make & document libraries.
#    

####################################
# Libraries
####################################
#I2C library
import smbus

#GPIO
import RPi.GPIO as GPIO

#Other
import time, os


####################################
#        User Parameters
#    (Edit these as necessary)
####################################
#Set LIS331 address
addr = 0x19

#Set the acceleration range
maxScale = 24

#Set the LED GPIO pin
LED = 26

#Open file to save all data
#(creates new file if none and appends to existing file)
allData = open("AllSensorData.txt", "a")

#Open file to save alert data
#(creates new file if none and appends to existing file)
alrtData = open("AlertData.txt", "a")

####################################
# Initializations & Functions
####################################
# Create I2C bus
bus = smbus.SMBus(1)

#Initialize GPIO and turn GPIO 26 to low
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED, GPIO.OUT)
GPIO.output(LED, GPIO.LOW)

#Initiliaze LIS331
def initialize(addr, maxScale):
    scale = int(maxScale)
    #Initialize accelerometer control register 1: Normal Power Mode and 50 Hz sample rate
    bus.write_byte_data(addr, 0x20, 0x27)
    #Initialize acceleromter scale selection (6g, 12 g, or 24g). This example uses 24g
    if maxScale == 6:
        bus.write_byte_data(addr, 0x23, 0x00)
    elif maxScale == 12:
        bus.write_byte_data(addr, 0x23, 0x10)
    elif maxScale == 24:
        bus.write_byte_data(addr, 0x23, 0x30)
    else:
        print "Error in the scale provided -- please enter 6, 12, or 24"


#Function to read the data from accelerometer
def readAxes(addr):
    data0 = bus.read_byte_data(addr, 0x28)
    data1 = bus.read_byte_data(addr, 0x29)
    data2 = bus.read_byte_data(addr, 0x2A)
    data3 = bus.read_byte_data(addr, 0x2B)
    data4 = bus.read_byte_data(addr, 0x2C)
    data5 = bus.read_byte_data(addr, 0x2D)
    #Combine the two bytes and leftshit by 8
    x = data0 | data1 << 8
    y = data2 | data3 << 8
    z = data4 | data5 << 8
    #in case overflow
    if x > 32767 :
        x -= 65536
    if y > 32767:
        y -= 65536
    if z > 32767 :
        z -= 65536
    #Calculate the two's complement as indicated in the datasheet
    x = ~x
    y = ~y
    z = ~z
    return x, y, z

#Function to calculate g-force from acceleration data
def convertToG(maxScale, xAccl, yAccl, zAccl):
    #Caclulate "g" force based on the scale set by user
    #Eqn: (2*range*reading)/totalBits (e.g. 48*reading/2^16)
    X = (2*float(maxScale) * float(xAccl))/(2**16);
    Y = (2*float(maxScale) * float(yAccl))/(2**16);
    Z = (2*float(maxScale) * float(zAccl))/(2**16);
    return X, Y, Z

def isDanger(timestamp, x, y, z):
    counter = 0
    x = long(x)
    y = long(y)
    z = long(z)

    if abs(x) > 9 or abs(y) > 9 or abs(z) > 9:
            alrtData.write(str(timestamp) + "\t" + "x: " + str(x) + "\t" + "y: " + str(y) + "\t" + "z: " +  str(z) + "\n")         
            GPIO.output(LED, GPIO.HIGH)
    elif abs(x) > 4 or abs(y) > 4 or abs(z) > 4:
            while abs(x) > 4 or abs(y) > 4 or abs(z) > 4:
                time_start = time.time()
                counter = counter + 1
                if counter > 4:
                    break
            time_end = time.time()
            if (counter > 4):
                alrtData.write(str(timestamp) + "\t" + "x: " + str(x) + "\t" + "y: " + str(y) + "\t" + "z: " + str(z) + "\n")
                GPIO.output(LED, GPIO.HIGH)

####################################
#       Main Function
####################################
def main():
    print ("Starting stream")
    while True:
        #initialize LIS331 accelerometer
        initialize(addr, 24)

        #Start timestamp
        ts = time.ctime()
        
        #Write timestamp to AllSensorData file 
        allData.write(str(ts) + "\t")

        #Get acceleration data for x, y, and z axes
        xAccl, yAccl, zAccl = readAxes(addr)
        #Calculate G force based on x, y, z acceleration data
        x, y, z = convertToG(maxScale, xAccl, yAccl, zAccl)
        #Determine if G force is dangerous to human body & take proper action
        isDanger(ts, x, y, z)

        #Write all sensor data to file AllSensorData (as you probably guessed :) )
        allData.write("x: " + str(x) + "\t" + "y: " + str(y) + "\t" + "z: " + str(z) + "\n")

        #print G values (don't need for full installation)
        print "Acceleration in X-Axis : %d" %x
        print "Acceleration in Y-Axis : %d" %y
        print "Acceleration in Z-Axis : %d" %z
        print "\n"

        #Short delay to prevent overclocking computer
        time.sleep(0.2)

    #Run this program unless there is a keyboard interrupt
    try:
        while True:
            pass
    except KeyboardInterrupt:
        myprocess.kill()
        allData.close()
        alrtData.close()
        GPIO.cleanup()


if __name__ =="__main__":
    main()
    allData.close()
    alrtData.close()
    GPIO.cleanup()

