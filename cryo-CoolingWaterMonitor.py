# Victor Zhang, created August 15, 2018
# Cooling Water Flow Rate monitor, by reading data through the LabJack U3-Lv
# version 0.2.0
# Python

'''
Program Details: 

1. Measuring voltage from LabJack U3-LV through port FIO1
    > voltage comes from water flow rate monitor, but we halve the voltage because the original voltage from the monitor is too high for the LabJack U3-LV to handle; FIO1 receives the halved voltage; see cryo-LabJackU3LV-setup.png

2. Converting voltage to flow rate using relationship determined experimentally: voltage = ((flow rate * 0.25) + 1) / 2
    > or using flow rate = 4 * (2 * voltage - 1)

Notes: 

August 15, 2018, 16:26
    > Flow Rate monitor says flow rate is 6.9 L/min
    > Oscilloscope says voltage is 1.3 V (right on the line)
    > Program determines voltage is about 1.3 V, flow rate is calculate to be about 6.5 L/min
    > Wire from water flow rate monitor is connected to FIO1
    > When nothing is connected to ports FIO0 and FIO1, FIO0 and FIO1 have almost exactly the same noise levels, except that of FIO0 = FIO1 + 0.01 (approximate, this was experimentally measured); FIO1 has noise of about 0.14
    > When FIO1 is connected to water flow rate monitor, the noise in FIO0 is measured to be about 0.33

'''

import u3
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation

d = u3.U3() 
d.debug = True
d.getCalibrationData()
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
    file.write("{:10.7f},\n".format(flowRate[i]))    
        
    # below live updates the coolWaterFR variable in cryo-Environment-Data.dat 
    with open('cryo-Environment-Data.dat','r') as environ:
        data = environ.readlines() 

    data[29] = data[29][:data[29].index("=")+1] + " " + "{:5.3f}\n".format(flowRate[i])

    with open('cryo-Environment-Data.dat','w') as environ:
        environ.writelines(data)

    
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


