# Victor Zhang, created August 15, 2018
# Cooling Water Flow Rate monitor, by reading data through the LabJack U3-Lv
# version 0.1.0
# Python

import u3
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation

d = u3.U3() 
d.debug = True
print("getCalibrationData:")
print(d.getCalibrationData(),"\n")
print("configIO:")
print(d.configIO(), "\n")
d.configIO(FIOAnalog = 15)
print("configIO:")
print(d.configIO(), "\n")
fileName = 'cryo-WaterMeas.dat'

voltage = np.zeros(100000)
x = np.arange(100000)

def update(i):
#getAIN seems to be better, since it automatically changes the bits to volt for you
    print("voltage at %s: %s vs %s\n" % (i,d.getAIN(1),d.getAIN(0)))
    voltage[i]=d.getAIN(1) - d.getAIN(0) - 0.02
    file.write("{:10.7f},\n".format(voltage[i]))    
    # Wire from water flow rate monitor is connected to FIO1
    # FIO0 and FIO1 have almost exactly the same noise levels, expect that of FIO0 = FIO1 + 0.02 (approximate, this was experimentally measured)


    
file = open(fileName, 'w')
file.write("voltage,\n")

fig, ax = plt.subplots()
voltGraph, = ax.plot([], [], 'k-')
ax.margins(0.05)

def init():
    voltGraph.set_data(x[:2],voltage[:2])
    return voltGraph,

def animate(i):
    win = 100
    update(i)
    imin = min(max(0,i - win), len(x) - win)
    xdata = x[imin:i]
    voltGraphData = voltage[imin:i]
    voltGraph.set_data(xdata, voltGraphData)
    ax.relim()
    ax.autoscale()
    print(i)
    return voltGraph,

anim = animation.FuncAnimation(fig, animate, init_func=init, interval=100)

plt.show()
d.close()


