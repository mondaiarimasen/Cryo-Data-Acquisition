# Victor Zhang, created August 15, 2018
# Client side: Socket to get water flow rate
# version 1.0.0
# Python

import u3
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
import socket

i=0

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

local_hostname = socket.gethostname()

localfqdn = socket.getfqdn()

ip_address = "133.11.164.152" # IP Address of daq02, which is "central" computer

server_address = (ip_address, 9876)
sock.connect(server_address)
print("Connecting to %s (%s) at %s" % (local_hostname, localfqdn, ip_address))


d = u3.U3() 
d.debug = True
#d.getCalibrationData()
d.configIO(FIOAnalog = 15)
fileName = 'cryo-WaterMeas.dat' # name of file you want to save the calculated flow rate values to
flowRate = np.zeros(100000) # array to hold the calculated flow rate values 
voltage = np.zeros(100000) 
x = np.arange(100000)
sleepTime = 1000*5 # how often to take samples


def update(i):
    #getAIN seems to be better than reading the bits and converting, since it automatically changes the bits to volts for you
    print("voltage at %s: %s vs %s\n" % (i,d.getAIN(1),d.getAIN(0)))
    voltage[i]=d.getAIN(1) 
    flowRate[i] = 4 * (2 * voltage[i] - 1)
    formattedFR = "{:5.3f}\n".format(flowRate[i])
    file.write(formattedFR[:-2])
        
    # below live updates the coolWaterFR variable in cryo-Environment-Data.dat 
    with open('cryo-Environment-Data.dat','r') as environ:
        data = environ.readlines() 

    data[29] = data[29][:data[29].index("=")+1] + " " + formattedFR

    with open('cryo-Environment-Data.dat','w') as environ:
        environ.writelines(data)

    if(i < 10): # hardcoded limit of 10 sends before stopping the sending of any more data
        sock.sendall(formattedFR)
        print("after sendall, sent: %s" % formattedFR)
    elif (i == 10):
        print("%s, closing socket" % i)
        sock.sendall("done".encode())
        print("after sendall, sent: done")
        sock.close()
    else:
        pass

    
file = open(fileName, 'w')
file.write("coolWaterFR,\n")

fig, ax = plt.subplots()
voltGraph, = ax.plot([], [], 'k-')

figFR, axFR = plt.subplots()
flowGraph, = axFR.plot([], [], 'r-')

ax.margins(0.05)
axFR.margins(0.05)

def init():
    voltGraph.set_data(x[:2],voltage[:2])
    flowGraph.set_data(x[:2],flowRate[:2])
    return voltGraph,

def animate(i):
    win = 100
    update(i)
    imin = min(max(0,i - win), len(x) - win)
    xdata = x[imin:i]
    voltGraphData = voltage[imin:i]
    flowRateData = flowRate[imin:i]
    voltGraph.set_data(xdata, voltGraphData)
    flowGraph.set_data(xdata, flowRateData)
    ax.relim()
    ax.autoscale()
    axFR.relim()
    axFR.autoscale()
    print(i)
    return voltGraph,

anim = animation.FuncAnimation(fig, animate, init_func=init, interval=sleepTime)
animFR = animation.FuncAnimation(figFR, animate, init_func=init, interval=sleepTime)
plt.show()
d.close()


