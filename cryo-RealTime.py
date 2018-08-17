# Victor Zhang, created August 14, 2018
# Real Time Temperature Acquisition from Lake Shore 372 device
# version 2.0.0
# Python

## imports ##
import socket
from datetime import datetime, timedelta
import time
import numpy as np
import matplotlib.pyplot as plt

## Variables (change these as much as you like) ##
brght = 1 # brightness of LS372 display; 0=25%, 1=50%, 2=75%, 3=100%
date_time = "" # later holds current date and time 
allTemp = "" # later holds all the temp readings
sleepTime = 0.5 # how many seconds between temperature taking
stopDate = "2018-08-16" # write in %Y-%m-%d format, ex. 2018-08-16, or 2018-01-04, but NOT 18-8-6 NOR 18-1-4
stopHour = 22 # what hour (in 24 hours) want to stop; ex. if want to stop at 10:00, then stopHour = 10; if want to stop at 19:00, then stopHour = 19; stopHour is an int, don't make it a string
dataAmt = 100000 # amount of data points you anticipate (or want); you will get this many temperature readings of each channel; check if this is enough to reach the desired stopDate and stopHour based on your sleepTime
repeatlength = 20 # how many points on the x-axis you want
deg = 90 # rotation degree of x-axis tick labels; this is another x-axis label display option
staticXInt = 100 # display the x-axis tick label on the static graph every staticXInt number of data points
dontMove = False # static graph (you can see all data), set dontMove = True; shifting graph (fixed x-axis length), set dontMove = False

## Constants (please don't change the values of these) ##
ip_address = "192.168.0.12" # IP Address of LS372
lsPort = 7777 # port that LS372 can only communicate with
rdgst_dict = {"000":"Valid reading is present", "001":"CS OVL", "002":"VCM OVL", "004":"VMIX OVL", "008":"VDIF OVL", "016":"R. OVER", "032":"R. UNDER", "064":"T. OVER", "128":"T. UNDER"} # dictionary of RDGST readings and their meanings
term = "\r\n" # terminator command for sending commands to LS372; this is what the manual refers to when it says "terminator"

iterNum = 0 # not really constant, since the for loop below changes it, but the user should not change its value from 0

totChannelNum = 8
channelNames = ["PT2 Head", "PT2 Plate", "1 K Plate", "Still", "mK Plate Cernox", "PT1 Head", "PT1 Plate", "mk Plate RuOx"] # first element is channel 1, etc
graph_AllChannel_Name = 'realTimeGraph-allChannels.png' # image shows all the channels
line_AllChannels = np.empty(totChannelNum,dtype='object') # holds the line objects for the 8 Channels
colors = ['k-', 'r-', 'b-', 'y-', 'm-', 'c-', 'g-', 'ro-'] # colors used to color the 8 channels 
graph_Special_Proxy = [7, 2, 3, 5] # which channels I am using to proxy the temp in the respective graph
graph_Special_Name = ['realTime-PT1.png', 'realTime-PT2.png', 'realTime-1K.png', 'realTime-MK.png']
fig_Special = np.empty(len(graph_Special_Name),dtype='object') # holds the figure objects for the special graphs
ax_Special = np.empty(len(graph_Special_Name),dtype='object') # holds the axes objects for the special graphs
line_Special = np.empty(len(graph_Special_Name),dtype='object') # holds the line objects for the special graphs
file_Name = 'cryo-LS372-Temp.dat' ## Temperature from LS372 is saved to this file

chlTemp = np.zeros((dataAmt,totChannelNum)) + 300 # temp of 300K for all channels by default
recTime = np.empty(dataAmt,dtype='object') # holds the x-axis time & date labels
x = np.arange(dataAmt) # x values, from 0 to dataAmt-1, inclusive (in a bijective mapping to recTime elements)


##################################################################

## Starting socket communication ##
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (ip_address, lsPort)
sock.connect(server_address)
print("Connecting to %s at Port %s\n" % server_address)

# Identification query; gives: LSCI,MODEL372,LSA2245,1.3 #
sock.send("*IDN?" + term)
data = sock.recv(1024)
print("Identification: ")
if data:
    print("%s"% data)
else:
    print("no more data")
    print("-------------\n")

# Network Configuration query, read manual for what the output means #
sock.send("NETID?" + term)
data = sock.recv(1024)
print("Network Configuration: ")
if data:
    print("%s"% data)
else:
    print("no more data")
    print("-------------\n")

# Brightness #
print("Changing brightness to %s%%" % str((brght+1)*25))
sock.send("BRIGT " + str(brght) + term)
sock.send("BRIGT?" + term)
data = sock.recv(1024)
if data:
    print("Brightness is set to: %s%%\n" % str((int(data)+1)*25))
else:
    print("no more data")
    print("-------------\n")

# Self-Test query #
print("Self-Test query: Checking for errors (0 for none, 1 for errors found)")
sock.send("*TST?" + term)
data = sock.recv(1024)
if data:
    print("error: %s"% data)
else:
    print("no more data")
    print("-------------\n")

##################################################################

## Starting the data acquisition ##
file = open(file_Name, 'w')
file.write("Time,1,2,3,4,5,6,7,8,\n")
file.close()

# sets up the x-axis time labels #
def setTime():
    date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    date_timeObj = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S.%f')
    # this accounts for the time needed to go from fig = plt.figure() to actually plotting the first point this was used in testing because the time was off by a few milliseconds, and here I am setting up all the x axis labels; couldn't find a way to display the live time on the graph, so I'm approximating it here, but as I said, if it's off, it's off by milliseconds
    date_timeObj = date_timeObj + timedelta(milliseconds = sleepTime*2*1000+100) 
    print("setTime, making the x-labels")
    print("date_timeObj = date_time + %s: %s" % (sleepTime*1000, date_timeObj))
    recTime[0] = date_timeObj.strftime('%Y-%m-%d %H:%M:%S.%f')
    day = date_timeObj.day
    for i in range(1,len(recTime)):
        recTimeObj = datetime.strptime(recTime[i-1], '%Y-%m-%d %H:%M:%S.%f') + timedelta(milliseconds = sleepTime*1000)
        recTime[i] = recTimeObj.strftime('%Y-%m-%d %H:%M:%S.%f')[:-5]

# the combined graph, static
fig_AllChannels = plt.figure(figsize=(15,8))
ax_AllChannels = fig_AllChannels.add_subplot(1,1,1)
ax_AllChannels.set_ylim([0,310])

for i in range(0,len(graph_Special_Name)):
    fig_Special[i] = plt.figure(figsize=(15,8))
    ax_Special[i] = fig_Special[i].add_subplot(1,1,1)
    ax_Special[i].set_xlim([0,repeatlength])


setTime()
# for calibration/testing purposes
date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
print("date_time after fig, ax: %s\n" % date_time)

for i in range(0, len(colors)):
    line_AllChannels[i], = ax_AllChannels.plot([], [], colors[i])

for i in range(0, len(graph_Special_Name)):
    line_Special[i], = ax_Special[i].plot([], [], 'ro-')

#ax.margins(5)

print("while starting\n")
while stopDate != date_time[:len(stopDate)] or stopHour != int(date_time[11:13]):

    ## Part 1: getting the temperature and writing to file ##
    date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    print("iterNum: %s, date_time: %s" % (iterNum, date_time))
    print("Stopping on: %s at hour %s" % (stopDate, stopHour))
    allTemp = date_time + ","

    print("Status and Reading of Thermometers:")
    for j in range(0,totChannelNum):
        # sees if the channel being read is responsive (not checking the code, but can do so; dictionary is in constants section at top of file)
        command = "RDGST? " + str(j+1) + term
        sock.send(command)
        data = sock.recv(1024)[:-2]
        if data:
            pass
        else:
            print("Error at Channel %s (RDGST? command)" % str(j+1))
            print("-------------\n")

        # this actually gets the temperature of the channel
        # interestingly, there is another Kelvin Reading Query: KRDG?, see manual
        command2 = "RDGK? " + str(j+1) + term 
        sock.send(command2)
        data = sock.recv(1024)[:-2]
        if data:
            pass
        else:
            print("Error at Channel %s (RDGK? command)" % str(j+1))
            print("-------------\n")
        chlTemp[iterNum:iterNum+1,j:j+1] = -1*((300 - float(data))%300) + 300
        print("chlTemp[iterNum:iterNum+1,j:j+1]: %s" % chlTemp[iterNum:iterNum+1,j:j+1][0][0])
        print("str(chlTemp[iterNum:iterNum+1,j:j+1]): %s" % str(chlTemp[iterNum:iterNum+1,j:j+1][0][0]))
        allTemp += str(chlTemp[iterNum:iterNum+1,j:j+1][0][0]) + ","
    print("chlTemp[9:10,:]: %s" % chlTemp[9:10,:])
    print("allTemp: %s" % allTemp)
    file = open(file_Name, 'a')
    file.write(allTemp + "\n")
    file.close()

    ## Part 2: drawing the plot and saving the image ##
    
    # Plotting the graph with all channels #
    imin = min(max(0,iterNum - repeatlength), len(x) - repeatlength)
    print("In dontMove True: %s" % dontMove)
    for j in range(0,totChannelNum):
        line_AllChannels[j].set_xdata(x[:iterNum])
        line_AllChannels[j].set_ydata(chlTemp[:iterNum,j:j+1])
    ax_AllChannels.xaxis.set_ticks(x[:iterNum:staticXInt])
    ax_AllChannels.set_xticklabels(recTime[:iterNum:staticXInt])#,rotation=deg) # can use this instead if don't like plt.gcf().autofmt_xdate(), but warning that rotation of any deg other than 90 can result in confusion, since the tick mark is centered on the horizontal projection of oblique tick label
    ax_AllChannels.set_xlim(0,iterNum)
    ax_AllChannels.set_title("Real Time Temperature of All Channels of Cryostat - Static")
    ax_AllChannels.legend(channelNames,loc=2, bbox_to_anchor=(0.80, 0.9),fancybox=False, shadow=False, ncol=1)
    for label in ax_AllChannels.get_xmajorticklabels():
        label.set_rotation(30)
        label.set_horizontalalignment("right")
    fig_AllChannels.savefig(graph_AllChannel_Name)

    # Plotting Special Graphs #
    print("In dontMove False: %s" % dontMove)
    for j in range(0,len(graph_Special_Name)):
        line_Special[j].set_xdata(x[imin:iterNum])
        line_Special[j].set_ydata(chlTemp[imin:iterNum,graph_Special_Proxy[j]-1:graph_Special_Proxy[j]])
        ax_Special[j].xaxis.set_ticks(x[imin:iterNum])
        ax_Special[j].set_xticklabels(recTime[imin:iterNum])#,rotation=deg) # can use this instead if don't like plt.gcf().autofmt_xdate(), but warning that rotation of any deg other than 90 can result in confusion, since the tick mark is centered on the horizontal projection of oblique tick label
        ax_Special[j].relim()
        ax_Special[j].autoscale()
        if iterNum>repeatlength:
            ax_Special[j].set_xlim(iterNum-repeatlength,iterNum)
        else:
            ax_Special[j].set_xlim(0,repeatlength)

        print("plotting")
        ax_Special[j].set_title("Real Time Temperature of " + channelNames[graph_Special_Proxy[j]-1] + " (Channel " + str(graph_Special_Proxy[j]) + " is proxy)")
        for label in ax_Special[j].get_xmajorticklabels():
            label.set_rotation(30)
            label.set_horizontalalignment("right")

    plt.xlabel("Date and Time")
    plt.ylabel("Temperature (K)")
    #plt.gcf().autofmt_xdate() # makes x-axis labels look nice, but the first label may stretch pretty far past the y-axis, so it might be undesirable; I have rotation=deg available above in ax.set_xticklabels()
    plt.gcf().subplots_adjust(bottom=0.5)
    plt.tight_layout()    
    plt.draw()
    
    for j in range(0, len(graph_Special_Name)):
        fig_Special[j].savefig(graph_Special_Name[j])

    iterNum += 1
    print("Just saved to all %s\n" % graph_Special_Name)
    plt.pause(sleepTime) # waits sleepTime amount of seconds before taking sample again
    ## end of one while loop iteration (you can breathe) 

print("end of while")

sock.close()
