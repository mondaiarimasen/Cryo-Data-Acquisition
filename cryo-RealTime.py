# Victor Zhang, created August 14, 2018
# Real Time Temperature Acquisition from Lake Shore 372 device
# version 4.0.0
# Python

## imports ##
import socket
from datetime import datetime, timedelta
import time
import numpy as np
import matplotlib.pyplot as plt
import serial # used to read temperature, pressure, and relative humidity from serial port, send by Arduino
import u3 # needed to monitor cooling water (for LabJack U3-LV)

## Variables (change these as much as you like) ##
brght = 1 # brightness of LS372 display; 0=25%, 1=50%, 2=75%, 3=100%
date_time = "" # later holds current date and time 
allTemp = "" # later holds all the temp readings
sleepTime = 80 # how many seconds between temperature taking; NOTE: the program default adds 10 seconds between measured times; e.g. if you want to measure data every 90 secs, set sleepTime = 80
stopDate = "2018-08-24" # write in %Y-%m-%d format, ex. 2018-08-16, or 2018-01-04, but NOT 18-8-6 NOR 18-1-4
stopHour = 22 # what hour (in 24 hours) want to stop; ex. if want to stop at 10:00, then stopHour = 10; if want to stop at 19:00, then stopHour = 19; stopHour is an int, don't make it a string
dataAmt = 1000000 # amount of data points you anticipate (or want); you will get this many temperature readings of each channel; check if this is enough to reach the desired stopDate and stopHour based on your sleepTime
repeatlength = 20 # how many points on the x-axis you want
deg = 90 # rotation degree of x-axis tick labels; this is another x-axis label display option
staticXInt = 100 # display the x-axis tick label on the static graph every staticXInt number of data points

## Constants (please don't change the values of these) ##
ip_address = "192.168.0.12" # IP Address of LS372
lsPort = 7777 # port that LS372 can only communicate with
rdgst_dict = {"000":"Valid reading is present", "001":"CS OVL", "002":"VCM OVL", "004":"VMIX OVL", "008":"VDIF OVL", "016":"R. OVER", "032":"R. UNDER", "064":"T. OVER", "128":"T. UNDER"} # dictionary of RDGST readings and their meanings
term = "\r\n" # terminator command for sending commands to LS372; this is what the manual refers to when it says "terminator"

iterNum = 0 # not really constant, since the for loop below changes it, but the user should not change its value from 0

totChannelNum = 8 # to avoid hardcoding in the number of channels
channelNames = ["PT2 Head", "PT2 Plate", "1 K Plate", "Still", "mK Plate Cernox", "PT1 Head", "PT1 Plate", "mk Plate RuOx"] # first element is channel 1, etc

graph_AllChannel_Name = 'realTime-allChannels.png' # image shows all the channels
line_AllChannels = np.empty(totChannelNum,dtype='object') # holds the line objects for the 8 Channels (for plotting)

colors = ['k-', 'r-', 'b-', 'y-', 'm-', 'c-', 'g-', 'ro-'] # colors used to color the 8 channels 

graph_Special_Proxy = [7, 2, 3, 5] # which channels I am using to proxy the temp in the respective graph
graph_Special_Name = ['realTime-PT1.png', 'realTime-PT2.png', 'realTime-1K.png', 'realTime-MK.png']
fig_Special = np.empty(len(graph_Special_Name),dtype='object') # holds the figure objects for the special graphs (for plotting)
ax_Special = np.empty(len(graph_Special_Name),dtype='object') # holds the axes objects for the special graphs (for plotting)
line_Special = np.empty(len(graph_Special_Name),dtype='object') # holds the line objects for the special graphs (for plotting)

graph_TPH_Proxy = ["Temperature (C)", "Pressure (HPa)", "Humidity (%)"] # names of data value measured in respective graph
graph_TPH_Name = ['realTime-LabTemp.png', 'realTime-LabPres.png', 'realTime-LabHum.png']
fig_TPH = np.empty(len(graph_TPH_Name),dtype='object') # for lab temp, pres, and hum graphs
ax_TPH = np.empty(len(graph_TPH_Name),dtype='object') 
line_TPH = np.empty(len(graph_TPH_Name),dtype='object') 

graph_WaterFR_Name = 'realTime-WaterFR.png' # image show the water flow rate over time

file_LS372Temp_Name = 'cryo-LS372-Temp.dat' ## Temperature from LS372 is saved to this file
file_LabTPH_Name = 'cryo-Lab-TPH.dat' ## Temperature, Pressure, and Relative Humidity of the lab room is saved to this file
file_WaterFR_Name = 'cryo-WaterMeas.dat' # calculated flow rate values saved here

waterFR = np.zeros(dataAmt,dtype=float)
labTPH = np.zeros((dataAmt,len(graph_TPH_Name))) # holds values of lab temp, pres, and hum
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
file_LS372Temp = open(file_LS372Temp_Name, 'w')
file_LS372Temp.write("Time,1,2,3,4,5,6,7,8,\n")
file_LS372Temp.close()

file_LabTPH = open(file_LabTPH_Name, 'w')
file_LabTPH.write("Time,Temperature(C),Pressure(HPa),RelativeHumidity(%),\n")
file_LabTPH.close()

file_WaterFR = open(file_WaterFR_Name, 'w')
file_WaterFR.write("Time,WaterFlowRate(L/min),\n")
file_WaterFR.close()

# sets up the x-axis time labels #
def setTime():
    date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') #.%f') # if want to see microseconds, add .%f after %S, but need to add it everywhere the time shows up
    date_timeObj = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S') #.%f')
    # this accounts for the time needed to go from fig = plt.figure() to actually plotting the first point this was used in testing because the time was off by a few milliseconds, and here I am setting up all the x axis labels; couldn't find a way to display the live time on the graph, so I'm approximating it here, but as I said, if it's off, it's off by milliseconds
    date_timeObj = date_timeObj + timedelta(milliseconds = sleepTime*2*1000+100) 
    print("setTime, making the x-labels")
    print("date_timeObj = date_time + %s: %s" % (sleepTime*1000, date_timeObj))
    recTime[0] = date_timeObj.strftime('%Y-%m-%d %H:%M:%S') #.%f')
    day = date_timeObj.day
    for i in range(1,len(recTime)):
        recTimeObj = datetime.strptime(recTime[i-1], '%Y-%m-%d %H:%M:%S') + timedelta(milliseconds = sleepTime*1000)
        recTime[i] = recTimeObj.strftime('%Y-%m-%d %H:%M:%S')

# reads temperature, pressure, and relative humidity from Arduino, and records to file_LabTPH_Name #
def recTPH(time, i):
    print("in recTPH")
    ser = serial.Serial()
    ser.port = '/dev/ttyACM0'
    ser.open()
    serialOutput = ser.readline() 
    serialOutput = serialOutput.rstrip()
    outputArr = serialOutput.split(',')
    comments = ""
    print("TPH: %s,%s\n" % (len(serialOutput), serialOutput))
    ser.close()
    try:
        for j in range(0,len(graph_TPH_Name)):
            labTPH[i:i+1,j:j+1] = outputArr[j]
    except Exception as e:
        reg = [25.62,1012.02,62.00]
        for j in range(0,len(graph_TPH_Name)):
            labTPH[i:i+1,j:j+1] = reg[j]
        comments += "Exception here: " + str(e) + ","
        
    
    file_LabTPH = open(file_LabTPH_Name, 'a')
    file_LabTPH.write(time + "," + serialOutput + "," + comments + "\n")
    file_LabTPH.close()

    with open('cryo-Environment-Data.dat','r') as environ:
        data = environ.readlines() 

    for j in range(0, len(graph_TPH_Name)):
        data[37+j*4] = data[37+j*4][:data[37+j*4].index("=")+1] + " " + "{:3.2f}\n".format(labTPH[i:i+1,j:j+1][0][0])

    with open('cryo-Environment-Data.dat','w') as environ:
        environ.writelines(data)
    print("exiting recTPH")

   
def getWaterFR(time, i):
    print("in getWaterFR")
    d = u3.U3()
    d.debug = True
    d.getCalibrationData()
    d.configIO(FIOAnalog = 15)
    voltage = d.getAIN(1)
    waterFR[i] = (voltage - 0.5) / 0.119
    d.close()

    file_WaterFR = open(file_WaterFR_Name, 'a')
    file_WaterFR.write(time + "," + "{:5.3f},\n".format(waterFR[i]))
    file_WaterFR.close()

    with open('cryo-Environment-Data.dat','r') as environ:
        data = environ.readlines() 

    data[29] = data[29][:data[29].index("=")+1] + " " + "{:5.3f}\n".format(waterFR[i])

    with open('cryo-Environment-Data.dat','w') as environ:
        environ.writelines(data)
    print("exiting getWaterFR")
    
## Starting the Figures ## 
# the combined graph, static
fig_AllChannels = plt.figure(figsize=(15,8))
ax_AllChannels = fig_AllChannels.add_subplot(1,1,1)
ax_AllChannels.set_ylim([0,310])

for i in range(0, len(colors)):
    line_AllChannels[i], = ax_AllChannels.plot([], [], colors[i])

# Special graphs #
for i in range(0,len(graph_Special_Name)):
    fig_Special[i] = plt.figure(figsize=(15,8))
    ax_Special[i] = fig_Special[i].add_subplot(1,1,1)
    ax_Special[i].set_xlim([0,repeatlength])

for i in range(0, len(graph_Special_Name)):
    line_Special[i], = ax_Special[i].plot([], [], 'ko-')

# TPH graph #
for i in range(0,len(graph_TPH_Name)):
    fig_TPH[i] = plt.figure(figsize=(15,8))
    ax_TPH[i] = fig_TPH[i].add_subplot(1,1,1)
    ax_TPH[i].set_xlim([0,repeatlength])

for i in range(0, len(graph_TPH_Name)):
    line_TPH[i], = ax_TPH[i].plot([], [], 'ko-')

# WaterFR graph #
fig_WaterFR = plt.figure(figsize=(15,8))
ax_WaterFR = fig_WaterFR.add_subplot(1,1,1)
ax_WaterFR.set_xlim([0,repeatlength])
line_WaterFR, = ax_WaterFR.plot([],[],'ko-')

## End of initializing Figures ##
## Getting time ready ##
setTime()
# for calibration/testing purposes
date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print("date_time after fig, ax: %s\n" % date_time)

## Starting Data Collection ##
print("while starting\n")
while stopDate != date_time[:len(stopDate)] or stopHour != int(date_time[11:13]):

    ## Part 1: getting the temperature and writing to file ##
    date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("iterNum: %s, date_time: %s" % (iterNum, date_time))
    print("Stopping on: %s at hour %s" % (stopDate, stopHour))
    allTemp = date_time + ","
    
    recTPH(date_time, iterNum)
    getWaterFR(date_time, iterNum)

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
    file_LS372Temp = open(file_LS372Temp_Name, 'a')
    file_LS372Temp.write(allTemp + "\n")
    file_LS372Temp.close()

    ## Part 2: drawing the plot and saving the image ##
    
    # Plotting the graph with all channels #
    imin = min(max(0,iterNum - repeatlength), len(x) - repeatlength)
    print("In AllChannels")
    for j in range(0,totChannelNum):
        line_AllChannels[j].set_xdata(x[:iterNum])
        line_AllChannels[j].set_ydata(chlTemp[:iterNum,j:j+1])
    ax_AllChannels.xaxis.set_ticks(x[:iterNum:staticXInt])
    ax_AllChannels.set_xticklabels(recTime[:iterNum:staticXInt])#,rotation=deg) # can use this instead if don't like plt.gcf().autofmt_xdate() or label.set_rotation below, but warning that rotation of any deg other than 90 can result in confusion, since the tick mark is centered on the horizontal projection of oblique tick label
    ax_AllChannels.set_xlim(0,iterNum)
    print("plotting AllChannels")
    ax_AllChannels.set_title("Real Time Temperature of All Channels of Cryostat - Static")
    ax_AllChannels.set_ylabel("Temperature (K)")
    ax_AllChannels.legend(channelNames,loc=2, bbox_to_anchor=(0.80, 0.9),fancybox=False, shadow=False, ncol=1)
    # below for loop makes the x-axis labels have a nice slant
    for label in ax_AllChannels.get_xmajorticklabels():
        label.set_rotation(30)
        label.set_horizontalalignment("right")
    fig_AllChannels.savefig(graph_AllChannel_Name)

    # Plotting Special Graphs #
    print("In Special")
    for j in range(0,len(graph_Special_Name)):
        line_Special[j].set_xdata(x[imin:iterNum])
        line_Special[j].set_ydata(chlTemp[imin:iterNum,graph_Special_Proxy[j]-1:graph_Special_Proxy[j]])
        ax_Special[j].xaxis.set_ticks(x[imin:iterNum])
        ax_Special[j].set_xticklabels(recTime[imin:iterNum])#,rotation=deg) # can use this instead if don't like plt.gcf().autofmt_xdate() or label.set_rotation, but warning that rotation of any deg other than 90 can result in confusion, since the tick mark is centered on the horizontal projection of oblique tick label
        ax_Special[j].relim()
        ax_Special[j].autoscale()
        if iterNum>repeatlength:
            ax_Special[j].set_xlim(iterNum-repeatlength,iterNum)
        else:
            ax_Special[j].set_xlim(0,repeatlength)

        print("plotting Special")
        ax_Special[j].set_title("Real Time Temperature of " + channelNames[graph_Special_Proxy[j]-1] + " (Channel " + str(graph_Special_Proxy[j]) + " is proxy)")
        ax_Special[j].set_ylabel("Temperature (K)")
        # below for loop makes the x-axis labels have a nice slant
        for label in ax_Special[j].get_xmajorticklabels():
            label.set_rotation(30)
            label.set_horizontalalignment("right")

    # Plotting TPH Graph #
    print("In TPH")
    for j in range(0,len(graph_TPH_Name)):
        line_TPH[j].set_xdata(x[imin:iterNum])
        line_TPH[j].set_ydata(labTPH[imin:iterNum,j:j+1])
        ax_TPH[j].xaxis.set_ticks(x[imin:iterNum])
        ax_TPH[j].set_xticklabels(recTime[imin:iterNum])#,rotation=deg) # can use this instead if don't like plt.gcf().autofmt_xdate() or label.set_rotation, but warning that rotation of any deg other than 90 can result in confusion, since the tick mark is centered on the horizontal projection of oblique tick label
        ax_TPH[j].relim()
        ax_TPH[j].autoscale()
        if iterNum>repeatlength:
            ax_TPH[j].set_xlim(iterNum-repeatlength,iterNum)
        else:
            ax_TPH[j].set_xlim(0,repeatlength)

        print("plotting TPH")
        ax_TPH[j].set_title(graph_TPH_Proxy[j] + " of Lab")
        ax_TPH[j].set_ylabel(graph_TPH_Proxy[j])
        # below for loop makes the x-axis labels have a nice slant
        for label in ax_TPH[j].get_xmajorticklabels():
            label.set_rotation(30)
            label.set_horizontalalignment("right")

    # Plotting WaterFR Graph #
    print("In WaterFR")
    line_WaterFR.set_xdata(x[imin:iterNum])
    line_WaterFR.set_ydata(waterFR[imin:iterNum])
    ax_WaterFR.xaxis.set_ticks(x[imin:iterNum])
    ax_WaterFR.set_xticklabels(recTime[imin:iterNum])#,rotation=deg) # can use this instead if don't like plt.gcf().autofmt_xdate() or label.set_rotation, but warning that rotation of any deg other than 90 can result in confusion, since the tick mark is centered on the horizontal projection of oblique tick label
    ax_WaterFR.relim()
    ax_WaterFR.autoscale()
    if iterNum>repeatlength:
        ax_WaterFR.set_xlim(iterNum-repeatlength,iterNum)
    else:
        ax_WaterFR.set_xlim(0,repeatlength)

    print("plotting WaterFR")
    ax_WaterFR.set_title("Cooling Water Flow Rate")
    ax_WaterFR.set_ylabel("Flow Rate (L/min)")
    # below for loop makes the x-axis labels have a nice slant
    for label in ax_WaterFR.get_xmajorticklabels():
        label.set_rotation(30)
        label.set_horizontalalignment("right")

    plt.xlabel("Date and Time")
    #plt.gcf().autofmt_xdate() # makes x-axis labels look nice, but the first label may stretch pretty far past the y-axis, so it might be undesirable; I have rotation=deg available above in ax.set_xticklabels(); another option is label.set_rotation
    plt.gcf().subplots_adjust(bottom=0.5)
    plt.tight_layout()    
    plt.draw()

    # Saving graphs #
    for j in range(0, len(graph_Special_Name)):
        fig_Special[j].savefig(graph_Special_Name[j])
    for j in range(0, len(graph_TPH_Name)):
        fig_TPH[j].savefig(graph_TPH_Name[j])
    fig_WaterFR.savefig(graph_WaterFR_Name)

    iterNum += 1
    print("Just saved to all %s\n" % graph_Special_Name)
    print("Sleeping for %s seconds" % sleepTime)
    #time.sleep(sleepTime)
    plt.pause(sleepTime) # waits sleepTime amount of seconds before taking sample again; interestingly, the recorded time delay on cryo-LS372-Temp.dat is twice that of sleepTime, even if you use time.sleep()
    ## end of one while loop iteration (you can breathe) 

print("end of while")

sock.close()
