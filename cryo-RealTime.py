# Victor Zhang, created August 14, 2018
# Real Time Temperature Acquisition from Lake Shore 372 device
# version 1.0.0
# Python

import socket
from datetime import datetime, timedelta
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
import os, glob # used to check if graph exists; if does, remove and save new one

## Variables
ip_address = "192.168.0.12"
brght = 1 # 0=25%, 1=50%, 2=75%, 3=100%
date_time = ""
allTemp = ""
sleepTime = 1000*1 # how many milliseconds between temperature taking
stopDate = "2018-08-06" # write in %Y-%m-%d format
stopHour = 10 # what hour (in 24 hours) want to stop; ex. if want to stop at 10:00, then stopHour = 10
chlTemp = np.zeros(100000)
recTime = np.empty(100000,dtype='object') 
x = np.arange(100000)
repeatlength = 20 # how many points on the x-axis you want
deg = 90 # rotation degree of x-axis tick labels
staticXInt = 1 # display the x-axis tick label on the static graph every staticXInt number of data points
graphName = 'graphRealTime.png'

## Constants
rdgst_dict = {"000":"Valid reading is present", "001":"CS OVL", "002":"VCM OVL", "004":"VMIX OVL", "008":"VDIF OVL", "016":"R. OVER", "032":"R. UNDER", "064":"T. OVER", "128":"T. UNDER"}
term = "\r\n"

## Data file
fileName = 'cryo-LS372-Temp.dat'

## Starting socket communication
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
local_hostname = socket.gethostname()
localfqdn = socket.getfqdn()
server_address = (ip_address, 7777)
sock.connect(server_address)
print("Connecting to %s at Port %s" % server_address)

# Identification query; gives: LSCI,MODEL372,LSA2245,1.3
sock.send("*IDN?" + term)
data = sock.recv(1024)
print("Identification: ")
if data:
    print("%s"% data)
else:
    print("no more data")
    print("-------------\n")

# Network Configuration query
sock.send("NETID?" + term)
data = sock.recv(1024)
print("Network Configuration: ")
if data:
    print("%s"% data)
else:
    print("no more data")
    print("-------------\n")

# Brightness
print("Changing brightness to %s%%" % str((brght+1)*25))
sock.send("BRIGT " + str(brght) + term)
sock.send("BRIGT?" + term)
data = sock.recv(1024)
if data:
    print("Brightness is set to: %s%%" % str((int(data)+1)*25))
else:
    print("no more data")
    print("-------------\n")

# Self-Test query
print("Checking for errors (0 for none, 1 for errors found):")
sock.send("*TST?" + term)
data = sock.recv(1024)
if data:
    print("error: %s"% data)
else:
    print("no more data")
    print("-------------\n")

## Starting the data acquisition
file = open(fileName, 'w')
file.write("Time,1,2,3,4,5,6,7,8,\n")
file.close()

# sets up the x-axis time labels
def setTime():
    date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    date_timeObj = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S.%f')
    # this accounts for the time needed to go from fig = plt.figure() to actually plotting the first point this was used in testing because the time was off by a few milliseconds, and here I am setting up all the x axis labels; couldn't find a way to display the live time on the graph, so I'm approximating it here, but as I said, if it's off, it's off by milliseconds
    date_timeObj = date_timeObj + timedelta(milliseconds = sleepTime*2+100) 
    print("date_timeObj = date_time + %s: %s" % (sleepTime, date_timeObj))
    recTime[0] = date_timeObj.strftime('%Y-%m-%d %H:%M:%S.%f')
    day = date_timeObj.day
    for i in range(1,len(recTime)):
        recTimeObj = datetime.strptime(recTime[i-1], '%Y-%m-%d %H:%M:%S.%f') + timedelta(milliseconds = sleepTime)
        recTime[i] = recTimeObj.strftime('%Y-%m-%d %H:%M:%S.%f')[:-5]


def update(i):
    print("update begins")
    date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    print("First date_time: %s" % date_time)
    allTemp = date_time + ","

    print("Status and Reading of Thermometers:")
    for j in range(1,2):
        # sees if the channel being read is responsive (not checking the code, but can do so; dictionary is in constants section at top of file)
        command = "RDGST? " + str(j+1) + term
        sock.send(command)
        data = sock.recv(1024)[:-2]
        if data:
            pass
        else:
            print("Error at Channel %s (RDGST? command)" % str(i+1))
            print("-------------\n")

        # this actually gets the temperature of the channel
        # interestingly, there is another Kelvin Reading Query: KRDG?, see manual
        command2 = "RDGK? " + str(j+1) + term 
        sock.send(command2)
        data = sock.recv(1024)[:-2]
        allTemp += data +","
        if data:
            pass
        else:
            print("Error at Channel %s (RDGK? command)" % str(j+1))
            print("-------------\n")
        chlTemp[i] = float(data)
        file = open(fileName, 'a')
        file.write(date_time+",0," + "{:7.4f}".format(chlTemp[i]) + ",0,0,0,0,0,0,\n")
        file.close()
    print("allTemp: %s" % allTemp)
    print("update ends")
    #file.write(allTemp + "\n")
    
fig = plt.figure(figsize=(15,8))
ax = fig.add_subplot(1,1,1)
ax.set_xlim([0,repeatlength])
setTime()
# for calibration/testing purposes
date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
print("date_time after fig, ax: %s" % date_time)
line, = ax.plot([], [], 'ko-')
ax.margins(5)

def animate(i,dontMove):
    print("in animate")
    win = repeatlength
    print("first i: %s" % i)
    update(i)
    imin = min(max(0,i - win), len(x) - win)
    if dontMove:
        line.set_xdata(x[:i])
        line.set_ydata(chlTemp[0:i])
        ax.xaxis.set_ticks(x[:i:staticXInt])
        ax.set_xticklabels(recTime[:i:staticXInt]) #,rotation=deg) # can use this instead if don't like plt.gcf().autofmt_xdate(), but warning that rotation of any deg other than 90 can result in confusion, since the tick mark is centered on the horizontal projection of oblique tick label
        ax.relim()
        ax.autoscale()
        ax.set_xlim(0,i)
    else:
        line.set_xdata(x[imin:i])
        line.set_ydata(chlTemp[imin:i])
        ax.xaxis.set_ticks(x[imin:i])
        ax.set_xticklabels(recTime[imin:i]) #,rotation=deg) # can use this instead if don't like plt.gcf().autofmt_xdate(), but warning that rotation of any deg other than 90 can result in confusion, since the tick mark is centered on the horizontal projection of oblique tick label
        ax.relim()
        ax.autoscale()
        if i>repeatlength:
            ax.set_xlim(i-repeatlength,i)
        else:
            ax.set_xlim(0,repeatlength)
    print("in animate 2")
    print(i)
    print("leaving animate\n")
    return line,

#anim = animation.FuncAnimation(fig, animate(), interval=sleepTime, fargs=(False,)) 
anim = animation.FuncAnimation(fig, animate, fargs=(False,), interval=sleepTime, repeat=False)
for filename in glob.glob(graphName[:-4]+"*"):
    print("found")
print("plotting")
plt.title("Real Time Temperature of Channel 2 of Cryostat")
plt.xlabel("Date and Time")
plt.ylabel("Temperature (K)")
plt.gcf().autofmt_xdate()
plt.gcf().subplots_adjust(bottom=0.25)

#anim.save("animationframe.png")
plt.show()


sock.close()
#file.close()
