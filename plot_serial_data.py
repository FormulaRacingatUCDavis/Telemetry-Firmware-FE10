#!/usr/bin/env python

from threading import Thread
import serial
import time
import collections
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import struct
import sys
import copy

class serialPlot:
  def __init__(self, serialPort, serialBaud, plotLength, packetNumBytes, numDataTypes, typeNumVals, valNumBytes):
    self.port = serialPort
    self.baud = serialBaud
    self.packetNumBytes = packetNumBytes
    self.numDataTypes = numDataTypes
    self.typeNumVals = typeNumVals
    self.valNumBytes = valNumBytes
    self.rawData = bytearray(packetNumBytes)
    self.data = []
    for i in range(numDataTypes):
      self.data.append([])
      for j in range(typeNumVals[i]+1):  # array for each value of each type + time
        self.data[i].append(collections.deque([], maxlen=plotLength))
    self.isRun = True
    self.isReceiving = False
    self.thread = None
    self.prevData = None
    self.plotTimer = 0
    self.previousTimer = 0
    self.firstTime = 0

    print('Trying to connect to: ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
    try:
      self.serialConnection = serial.Serial(serialPort, serialBaud, timeout=4)
      print('Connected to ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
    except:
      sys.exit("Failed to connect with " + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')

  def readSerialStart(self):
    if self.thread == None:
      self.thread = Thread(target=self.backgroundThread)
      self.thread.start()
      # Block till we start receiving values
      while self.isReceiving != True:
        time.sleep(0.1)

  def getSerialData(self, frame, ax, lines, lineValueText, lineLabel, timeText, timeRange):
    currData = copy.deepcopy(self.rawData[:])
    if currData == self.prevData:
      return
    currentTimer = time.perf_counter()
    self.plotTimer = int((currentTimer - self.previousTimer) * 1000)  # the first timer reading will be erroneous
    self.previousTimer = currentTimer
    timeText.set_text('Plot Interval = ' + str(self.plotTimer) + 'ms')
    dataId = struct.unpack('h', currData[:2])[0]
    newTime = struct.unpack('L', currData[10:14])[0] / 1000000  # microseconds to seconds
    self.data[dataId][0].append(newTime)
    for j in range(self.typeNumVals[dataId]):
      value = struct.unpack('h', currData[2+j*self.valNumBytes:2+(j+1)*self.valNumBytes])[0]
      self.data[dataId][j+1].append(value)
      lines[dataId][j].set_data(self.data[dataId][0], self.data[dataId][j+1])
      lineValueText[dataId][j].set_text('[' + lineLabel[j] + '] = ' + str(value))
    if self.prevData == None:
      self.firstTime = newTime
      ax[0].set_xbound(self.firstTime, self.firstTime + timeRange)
    elif (newTime - self.firstTime > timeRange):
      ax[0].set_xbound(newTime - timeRange, newTime)
    self.prevData = currData

  def backgroundThread(self):  # retrieve data continuously
    time.sleep(1.0)  # give some buffer time for retrieving data
    self.serialConnection.reset_input_buffer()
    while (self.isRun):
      self.serialConnection.readinto(self.rawData)
      self.isReceiving = True

  def close(self):
    self.isRun = False
    self.thread.join()
    self.serialConnection.close()
    print('Disconnected')

class Anim:
  def __init__(self, animationInit):
    self.anim = animationInit
    self.paused = False

  def togglePause(self, event):
    if self.paused:
      self.anim.resume()
    else:
      self.anim.pause()
    self.paused = not self.paused

def main():
  portName = 'COM4'
  baudRate = 38400
  maxPlotLength = 100
  timeRange = 10
  packetNumBytes = 14
  numDataTypes = 2
  typeNumVals = [4, 1]  # number of data values for each data type
  valNumBytes = 2
  s = serialPlot(portName, baudRate, maxPlotLength, packetNumBytes, numDataTypes, typeNumVals, valNumBytes)  # initializes all required variables
  s.readSerialStart()  # starts background thread
  time.sleep(1.5)

  # plotting starts below
  pltInterval = 10  # Period at which the plot animation updates [ms]
  xmin, xmax = (0, timeRange)
  ymin, ymax = (0 , 50)
  fig, ax = plt.subplots(numDataTypes, sharex=True)
  fig.set_figheight(5.4)
  plt.suptitle("ESP32 Data Processing")

  plotLabel = ['Wheel', 'Steering']
  lineLabel = ['a', 'b', 'c', 'd']
  style = ['r-', 'c-', 'b-', 'y-']  # colors for the different plots
  lines = []
  lineValueText = []
  leg = []
  ax[0].set_xbound(xmin, xmax)
  ax[numDataTypes-1].set_xlabel("Time")
  for i in range(numDataTypes):
    ax[i].set_ybound(float(ymin - (ymax - ymin) / 10), float(ymax + (ymax - ymin) / 10)) # extra range for y values
    ax[i].set_ylabel(plotLabel[i] + " Vals")
    lines.append([])
    lineValueText.append([])
    leg.append([])
    for j in range(typeNumVals[i]):
      lines[i].append(ax[i].plot([], [], style[j],)[0])
      lineValueText[i].append(ax[i].text(0.80, 0.90-j*0.08, '', transform=ax[i].transAxes))  # position text
      leg[i].append(plotLabel[i] + lineLabel[j])
    ax[i].legend(leg[i], loc="upper left")
  timeText = ax[0].text(0.35, 1.1, '', transform=ax[0].transAxes)
  anim = Anim(animation.FuncAnimation(fig, s.getSerialData, fargs=(ax, lines, lineValueText, lineLabel, timeText, timeRange), interval=pltInterval))
  fig.canvas.mpl_connect('key_press_event', anim.togglePause)
  plt.show()
  s.close()

if __name__ == '__main__':
  main()