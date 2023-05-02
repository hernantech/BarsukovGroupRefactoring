import visa
import time
import random
import socket
import zmq
import imp
import os
import glob
#import thread
import re
import numpy as np
import numpy
import scipy as sp
import datetime
from scipy.interpolate import interp1d
import pyqtgraph as pg
from PyDAQmx import *
import math
''' *** GENERAL WRAPPERS *** '''
def printN(q):
    print(q)
    pass
''' *** ---------------- *** '''    


''' *** COMMUNICATION *** '''
def getip():
    return socket.gethostbyname(socket.gethostname())

def initPubSocket(port):
    context = zmq.Context.instance()
    sock = context.socket(zmq.PUB)
    ip = getip()
    port = int(port)
    for j in range(0,10,1):
        fulladdr = 'tcp://' + ip + ':' + str(port)
        try:
            sock.bind(fulladdr)
            return sock, context, fulladdr, port
        except:
            port = random.randint(49152,65535)
            pass
    print('Could not establish a PUB socket in 10 attempts. ')
    quit()

def initSUBSocket(ip, port):
    context = zmq.Context.instance()
    sock = context.socket(zmq.SUB)
    port = int(port)
    for j in range(0,10,1):
        fulladdr = 'tcp://' + ip + ':' + str(port)
        try:
            sock.connect(fulladdr)
            sock.setsockopt_string(zmq.SUBSCRIBE, '')
            return sock, context, fulladdr, port
        except:
            port = input('Redefine port: ')
            pass
    print('Could not establish a SUB socket in 10 attempts. ')
    quit()
''' *** ------------- *** '''


''' *** DATA WRAPPERS *** '''
def forwback(x,y,step):
    list1 = np.arange(x,y,step)
    list2 = np.arange(y,x-step, -step)
    listV = np.concatenate((list1,list2))
    return listV

def forwback2(x,y,step,fx,fy,finestep):
    list1a = np.arange(x,fx,step)
    list1b = np.arange(fx,fy,finestep)
    list1c = np.arange(fy,y,step)
    list2a = np.arange(y,fy,-step)
    list2b = np.arange(fy,fx,-finestep)
    list2c = np.arange(fx,x-step,-step)
    listV = np.concatenate((list1a,list1b,list1c,list2a,list2b,list2c))
    return listV

''' *** ------------- *** '''


''' *** EQUIPMENT WRAPPERS *** '''
def initEq():
    rm = visa.ResourceManager()
    res = rm.list_resources()
    printN('List of instruments: '+str( res))
    return rm, res
    
precon = 'GPIB0::'



def eq(rm, con, typ):
    if typ == 'yokogawa':
        y = yokogawaGS200(rm, con)
        #print(y.idn())
        return y
    if typ == 'mwgen':
        y = AgilentPSG(rm, con)
        #print(y.idn())
        return y
    if typ == 'yokogawaGS200':
        y = yokogawaGS200(rm, con)
        #print(y.idn())
        return y
    if typ == 'nanovolt':
        y = NanoKeysight(rm, con)
        #print(y.idn())
        return y
    if typ == 'gauss':
        y = Gauss(rm, con)
        #print(y.idn())
        return y
    if typ == 'sr760':
        y = SR71BB(rm, con)
        #print(y.idn())
        return y
    if typ == 'lockin7265':
        y = lockin7265(rm, con)
        #print(y.idn())
        return y
    if typ == 'keithley6221':
        y = keithley6221(rm, con)
        #print(y.idn())
        return y

    if typ == 'cs580':
        y = cs580(rm, con)
        #print(y.idn())
        return y



    
    else: print('Could not find the Equipment Object in _meas_lib.py')
    
        #if typ == 'GPIB::11':
     #   y = GPIB::11(rm, con)
        #print(y.idn())
      #  return y
   # else: print('Could not find the Equipment Object in _meas_lib.py')
''' *** ------------------ *** '''


''' *** EQUIPMENT OBJECTS *** '''
class lockin7265():

    def __init__(self,rm,con):
        self.confull = precon + con
        self.dev = rm.open_resource(self.confull)

    def idn(self):
        try:
            q = self.dev.query('*idn?')
            return q
        except:
            return False
    def query(self,x):
        try:
            q = self.dev.query(x)
            return q
        except:
            return False
    def write(self,x):
        try:
            q = self.dev.write(x)
            return q
        except:
            return False
    def close(self):
        return self.dev.close()

    
    def liconsts(self, Amplitude, Frequency, Sensitivity, TimeConstant, Phase, ACGain,Imode):

        self.dev.write('OF {}'.format(Frequency * 1000))
        self.dev.write('OA {}'.format(Amplitude))
        self.dev.write('SEN {}'.format(Sensitivity))
        self.dev.write('TC {}'.format(TimeConstant))
        self.dev.write('REFP {}'.format(Phase * 1000))
        self.dev.write('ACGAIN {}'.format(ACGain))
        self.dev.write('IMODE {}'.format(Imode))
        


class keithley6221():
    def __init__(self, rm, con):
        self.confull = precon + con
        self.dev = rm.open_resource(self.confull)
    def idn(self):
        try:
            q = self.dev.query('*idn?')
            return q
        except:
            return False
    def query(self,x):
        try:
            q = self.dev.query(x)
            return q
        except:
            return False
    def write(self,x):
        try:
            q = self.dev.write(x)
            return q
        except:
            return False

        
    def level(self,x,y): #if y='on', the yoko will be switched on after sign change. otherwise it will not 
        try:
            reading = float( self.dev.query('CURRent?'))
            difference = x - reading
            if np.sign(x)*np.sign(reading)>0:
                #print(np.sign(x)*np.sign(reading))
                if np.abs(difference)>0.000010:
                    listlevel = np.arange(reading, x, np.sign(difference)*0.000010)
                    for j in listlevel:
                        self.dev.write('CURRent {}'.format(j))
                        time.sleep(0.500)
                self.dev.write('CURRent {}'.format(x))
                return self.dev.query('CURRent?')
            else:
                #print(np.sign(x)*np.sign(reading))
                listlevel = np.arange(reading, np.sign(reading)*0.000010, -np.sign(reading)*0.000010)
                for j in listlevel:
                    self.dev.write('CURRent {}'.format(j))
                    time.sleep(0.500)
                self.dev.write(':OUTPut OFF')
                time.sleep(1.000)
                self.dev.write('CURRent {}'.format(np.sign(x)*0.000010))
                #time.sleep(1.000)
                if y=='on':
                    self.dev.write('OUTPut ON')
                reading = float( self.dev.query('CURRent?'))
                difference = x - reading
                listlevel = np.arange(reading, x, np.sign(difference)*0.000010)
                for j in listlevel:
                    self.dev.write('CURRent {}'.format(j))
                    time.sleep(0.500)
                self.dev.write('CURRent {}'.format(x))
        except:
            return False

    def dcsafeoff(self):
        try:
            self.level(np.sign(float( self.dev.query('CURRent?')))*0.000010,'on')
            self.dev.write('OUTPut OFF')
            return self.dev.query('CURRent?')
        except:
            return False
        
    def dcsafeon(self, x):
        try:
            self.level(np.sign(float( self.dev.query('CURRent?')))*0.000010,'on')
            self.dev.write('OUTPut ON')
            self.level(x,'on')
            return self.dev.query('CURRent?')
        except:
            return False
        
    

##
##    def dcsafeoff (self):
##        I = float(self.dev.query ('CURRent?'))
##        if I>0:
##            for i in np.arange ( I, 0.01e-3, -0.01e-3 ):
##                self.dev.write ('CURRent {}'.format (i))
##                time.sleep(0.8)
##            self.dev.write ('CURRent {}'.format (0.01e-3))
##        else:
##            for i in np.arange ( I, -0.01e-3, 0.01e-3 ):
##                self.dev.write ('CURRent {}'.format (i))
##                time.sleep(0.8)
##            self.dev.write ('CURRent {}'.format (-0.01e-3))
##        self.dev.write ('OUTPut OFF')            
##
##    
##    def dcsafeon (self,x):
##        I = float(self.dev.query ('CURRent?'))
##        if x>0:
##            self.dev.write ('CURRent 0.01e-3')
##            time.sleep(0.5)
##            self.dev.write ('OUTPut ON')
##            for i in np.arange ( 0.01e-3, x, 0.01e-3 ):
##                self.dev.write ('CURRent {}'.format (i))
##                time.sleep(0.8)
##            self.dev.write ('CURRent {}'.format (x))
##        else:
##            self.dev.write ('CURRent -0.01e-3')
##            time.sleep(0.5)
##            self.dev.write ('OUTPut ON')
##            for i in np.arange ( -0.01e-3, x, -0.01e-3 ):
##                self.dev.write ('CURRent {}'.format (i))
##                time.sleep(0.8)
##            self.dev.write ('CURRent {}'.format (x))
##        self.dev.write ('OUTPut ON') 
##  
class cs580():
    def __init__(self, rm, con):
        self.confull = 'ASRL' + con + '::INSTR'
        self.dev = rm.open_resource(self.confull)
    def idn(self):
        try:
            q = self.dev.query('*idn?')
            return q
        except:
            return False
    def query(self,x):
        try:
            q = self.dev.query(x)
            return q
        except:
            return False
    def write(self,x):
        try:
            q = self.dev.write(x)
            return q
        except:
            return False

        
    def level(self,x,y): #if y='on', the yoko will be switched on after sign change. otherwise it will not 
        try:
            reading = float( self.dev.query('CURR?'))
            difference = x - reading
            if np.sign(x)*np.sign(reading)>0:
                #print(np.sign(x)*np.sign(reading))
                if np.abs(difference)>0.000010:
                    listlevel = np.arange(reading, x, np.sign(difference)*0.000010)
                    for j in listlevel:
                        self.dev.write('CURR {}'.format(j))
                        time.sleep(0.500)
                self.dev.write('CURR {}'.format(x))
                return self.dev.query('CURR?')
            else:
                #print(np.sign(x)*np.sign(reading))
                listlevel = np.arange(reading, np.sign(reading)*0.000010, -np.sign(reading)*0.000010)
                for j in listlevel:
                    self.dev.write('CURR {}'.format(j))
                    time.sleep(0.500)
                self.dev.write(':SOUT OFF')
                time.sleep(1.000)
                self.dev.write('CURR {}'.format(np.sign(x)*0.000010))
                #time.sleep(1.000)
                if y=='on':
                    self.dev.write('SOUT ON')
                reading = float( self.dev.query('CURR?'))
                difference = x - reading
                listlevel = np.arange(reading, x, np.sign(difference)*0.000010)
                for j in listlevel:
                    self.dev.write('CURR {}'.format(j))
                    time.sleep(0.500)
                self.dev.write('CURR {}'.format(x))
        except:
            return False

    def dcsafeoff(self):
        try:
            self.level(np.sign(float( self.dev.query('CURR?')))*0.000010,'on')
            self.dev.write('SOUT OFF')
            return self.dev.query('CURR?')
        except:
            return False
        
    def dcsafeon(self, x):
        try:
            self.level(np.sign(float( self.dev.query('CURR?')))*0.000010,'on')
            self.dev.write('SOUT ON')
            self.level(x,'on')
            return self.dev.query('CURR?')
        except:
            return False





class yokogawaGS200:
    def __init__(self, rm, con):
        self.confull = precon + con
        self.dev = rm.open_resource(self.confull)
        printN('=LIB=> Initialized: yokogawaGS200 at '+ str(self.dev.primary_address)+': '+ self.idn())
    def idn(self):
        try:
            q = self.dev.query('*idn?')
            return q
        except:
            return False
    def query(self,x):
        try:
            q = self.dev.query(x)
            return q
        except:
            return False
    def write(self,x):
        try:
            q = self.dev.write(x)
            return q
        except:
            return False
    def level(self,x,y): #if y='on', the yoko will be switched on after sign change. otherwise it will not 
        try:
            reading = float( self.dev.query(':source:level?'))
            difference = x - reading
            if np.sign(x)*np.sign(reading)>0:
                #print(np.sign(x)*np.sign(reading))
                if np.abs(difference)>0.000010:
                    listlevel = np.arange(reading, x, np.sign(difference)*0.000010)
                    for j in listlevel:
                        self.dev.write(':source:level {}'.format(j))
                        time.sleep(0.100)
                self.dev.write(':source:level {}'.format(x))
                return self.dev.query(':source:level?')
            else:
                #print(np.sign(x)*np.sign(reading))
                listlevel = np.arange(reading, np.sign(reading)*0.000010, -np.sign(reading)*0.000010)
                for j in listlevel:
                    self.dev.write(':source:level {}'.format(j))
                    time.sleep(0.100)
                self.dev.write(':output off')
                time.sleep(1.000)
                self.dev.write(':source:level {}'.format(np.sign(x)*0.000010))
                #time.sleep(1.000)
                if y=='on':
                    self.dev.write(':output on')
                reading = float( self.dev.query(':source:level?'))
                difference = x - reading
                listlevel = np.arange(reading, x, np.sign(difference)*0.000010)
                for j in listlevel:
                    self.dev.write(':source:level {}'.format(j))
                    time.sleep(0.100)
                self.dev.write(':source:level {}'.format(x))
        except:
            return False
        
    def safeOff(self):
        try:
            self.level(np.sign(float( self.dev.query(':source:level?')))*0.000010,'on')
            self.dev.write(':output off')
            return self.dev.query(':source:level?')
        except:
            return False
        
    def safeOn(self, x):
        try:
            self.level(np.sign(float( self.dev.query(':source:level?')))*0.000010,'on')
            self.dev.write(':output on')
            self.level(x,'on')
            return self.dev.query(':source:level?')
        except:
            return False

    def level_rapid(self,x,y): #if y='on', the yoko will be switched on after sign change. otherwise it will not 
        try:
            reading = float( self.dev.query(':source:level?'))
            difference = x - reading
            if np.sign(x)*np.sign(reading)>0:
                #print(np.sign(x)*np.sign(reading))
                if np.abs(difference)>0.000010:
                    listlevel = np.arange(reading, x, np.sign(difference)*0.010000)
                    for j in listlevel:
                        self.dev.write(':source:level {}'.format(j))
                        time.sleep(0.100)
                self.dev.write(':source:level {}'.format(x))
                return self.dev.query(':source:level?')
            else:
                #print(np.sign(x)*np.sign(reading))
                listlevel = np.arange(reading, np.sign(reading)*0.010000, -np.sign(reading)*0.010000)
                for j in listlevel:
                    self.dev.write(':source:level {}'.format(j))
                    time.sleep(0.100)
                self.dev.write(':output off')
                time.sleep(1.000)
                #time.sleep(1.000)
                if y=='on':
                    self.dev.write(':output on')
                    self.dev.write(':source:level {}'.format(np.sign(x)*0.010000))
                reading = float( self.dev.query(':source:level?'))
                difference = x - reading
                listlevel = np.arange(reading, x, np.sign(difference)*0.010000)
                for j in listlevel:
                    self.dev.write(':source:level {}'.format(j))
                    time.sleep(0.100)
                self.dev.write(':source:level {}'.format(x))
        except:
            return False
        
    def safeOff_rapid(self):
        try:
            self.level_rapid(np.sign(float( self.dev.query(':source:level?')))*0.000010,'on')
            self.dev.write(':output off')
            return self.dev.query(':source:level?')
        except:
            return False
        
    def safeOn_rapid(self, x):
        try:
            self.level_rapid(np.sign(float( self.dev.query(':source:level?')))*0.010000,'on')
            self.dev.write(':output on')
            self.level_rapid(x,'on')
            return self.dev.query(':source:level?')
        except:
            return False


class NanoKeysight():
    def __init__(self, rm, con):
        self.confull = precon + con
        self.dev = rm.open_resource(self.confull)
        #printN('=LIB=> Initialized: Keysight34420A at '+ str(self.dev.primary_address)+': '+ self.idn())
    def idn(self):
        try:
            q = self.query('*idn?')
            return q
        except:
            return False
    def query(self,x):
        try:
            q = self.dev.query(x)
            return q
        except:
            return False
    def write(self,x):
        try:
            print(x)
            q = self.dev.write(x)
            return q
        except:
            return False
    def initMR(self,samples):
        try:
            #self.timeout = 60000
            self.write(':sample:count {}'.format(samples))
            self.write(':trigger:source immediate')
            self.write(':trigger:delay 0')
            self.write(':trigger:count 1')
            return True
        except:
            return False
    def reading(self):
        try:
            readings = self.query(':read?')
            print('readings from within {}'.format(readings))
            list1 = readings[0:-1].split(',')
            list2 = []
            for j in list1:
                list2.append(float( j ))
            mean = np.mean( list2 )
            return mean
        except:
            return False


class AgilentPSG():
    def __init__(self,rm, con):
        self.confull = precon + con
        self.dev = rm.open_resource(self.confull)
        #printN('=LIB=> Initialized: AgilentPSG at '+ str(self.dev.primary_address)+': '+ self.idn())
    def idn(self):
        try:
            q = self.dev.query('*idn?')
            return q
        except:
            return False
    def query(self,x):
        try:
            q = self.dev.query(x)
            return q
        except:
            return False
    def write(self,x):
        try:
            q = self.dev.write(x)
            return q
        except:
            return False
    def freq(self,x):
        try:
            q = self.dev.write('freq {}GHz'.format(x))
            return q
        except:
            return False
    def close(self):
        return self.dev.close()

class Gauss():
    def __init__(self, rm, con):
        self.confull = precon + con
        self.dev = rm.open_resource(self.confull)
        #printN('=LIB=> Initialized: Keysight34420A at '+ str(self.dev.primary_address)+': '+ self.idn())
    def idn(self):
        try:
            q = self.query('*idn?')
            return q
        except:
            return False
    def query(self,x):
        try:
            q = self.dev.query(x)
            return q
        except:
            return False
    def write(self,x):
        try:
            print(x)
            q = self.dev.write(x)
            return q
        except:
            return False
    def channelV(self):
        try:
            self.write('chnl v')
            return True
        except:
            return False
    def readingV(self):
        try:
            readings = float( self.query(':field?') )
            return readings
        except:
            return False

class SR71BB():
    def __init__(self, rm, con):
        self.confull = precon + con
        self.dev = rm.open_resource(self.confull)
    
    def query(self,x):
        try:
            q = self.dev.query(x)
            return q
        except:
            return False
    def write(self,x):
        try:
            q = self.dev.write(x)
            return q
        except:
            return False

    def close(self):
        return self.dev.close()
    
    def measure(self):
        try:
            
            self.dev.clear()
            self.dev.write('strt\n')
            time.sleep(6)
            self.dev.clear()
            self.dev.write('auts 0\n')
            self.dev.write('strt\n')
            time.sleep(3)
            self.dev.write('strt\n')
            time.sleep(3)
            self.dev.write('strt\n')
            time.sleep(3)
            self.dev.clear()
            self.dev.write('strt\n')
            while self.dev.query("*stb?\n") != "17\n":
                time.sleep(1)
            self.dev.clear()
            srStringOP = self.dev.query('spec?0\n')
            return srStringOP.split(",")
        except:
            return (self.measure())
    
    def getSpectrum(self):
        try:
            
            singleMeas = self.measure()
            startF = float(self.query("BVAL?0,1\n"))
            freqStep = float(self.query("BVAL?0,1\n")) - float(self.query("BVAL?0,0\n"))

            dataR = np.ndarray(shape = (400,2), dtype = object)
            for i in range (400):
                tempArray = np.array([(i*freqStep + startF ),singleMeas[i]])
                dataR[i] = tempArray    
            return dataR
        except:
            return False
    def getSpectrumR(self, x = 0, y = 0):
        try:
            currFreq = x
            dataR = [(0,0)]
            span = (math.pow(2,float(self.dev.query('Span?\n')))*.19074)
            freqSweepSteps = int(((y-x)/span)+ 1)
            
            for i in range(freqSweepSteps):
                self.dev.write('STRF{}\n'.format(currFreq))
                time.sleep(.5)
                tempData = self.getSpectrum()
                dataR = np.concatenate((dataR, tempData), axis = 0)
                currFreq = currFreq + span
            return dataR

        except:
            #print(self.getSpectrum())
            return False
    def getFullSpectrum(self):
        try:
            currFreq = 0
            dataR = [(0,0)]
            span = (math.pow(2,float(self.dev.query('Span?\n')))*.19074)
            freqSweepSteps = int((100003)/span)
            
            for i in range(freqSweepSteps):
                self.dev.write('STRF{}\n'.format(currFreq))
                time.sleep(.5)
                tempData = self.getSpectrum()
                dataR = np.concatenate((dataR, tempData), axis = 0)
                currFreq = currFreq + span
                
            return dataR

        except:
            #print(self.getSpectrum())
            return False

    def appendRawData(self,data,gain):
        rData = np.array(data[:,1],dtype = 'float')/gain
        rData = np.array(rData, dtype = 'str')
        rData = np.reshape(rData,(data.shape[0],1))
        return np.concatenate((data,rData), axis = 1)
       
''' *** ----------------- *** '''


''' *** DAQ *** '''
def daqVinAve(chan,samples,VoltageRange): #Gets reading from channel of DAQ with samples_averaging

        taskHandle = TaskHandle()
        read = int32()
        data = numpy.zeros((samples,), dtype=numpy.float64)
        try:
                # DAQmx Configure Code
                DAQmxCreateTask("",byref(taskHandle))
                DAQmxCreateAIVoltageChan(taskHandle,"Dev1/ai" +str(chan),"",DAQmx_Val_Cfg_Default,-VoltageRange,VoltageRange,DAQmx_Val_Volts,None)

                # DAQmx Start Code
                DAQmxStartTask(taskHandle)

                # DAQmx Read Code
                DAQmxReadAnalogF64(taskHandle,samples,10.0,DAQmx_Val_GroupByChannel,data,samples,byref(read),None)

                #print "Acquired %d points"%read.value
        except DAQError as err:
                print("DAQmx Error: %s"%err)
        finally:
                if taskHandle:
                        # DAQmx Stop Code
                        DAQmxStopTask(taskHandle)
                        DAQmxClearTask(taskHandle)
        val = np.mean(data)
        return val

def daqVinAve2(chan1, chan2, samples, VoltageRange): #Gets reading from channel of DAQ with samples_averaging

        taskHandle = TaskHandle()
        read = int32()
        data = numpy.zeros((samples*2,), dtype=numpy.float64)
        try:
                # DAQmx Configure Code
                DAQmxCreateTask("",byref(taskHandle))
                DAQmxCreateAIVoltageChan(taskHandle,"Dev1/ai" +str(chan1),"",DAQmx_Val_Cfg_Default,-VoltageRange,VoltageRange,DAQmx_Val_Volts,None)
                DAQmxCreateAIVoltageChan(taskHandle,"Dev1/ai" +str(chan2),"",DAQmx_Val_Cfg_Default,-VoltageRange,VoltageRange,DAQmx_Val_Volts,None)
                # DAQmx Start Code
                DAQmxStartTask(taskHandle)

                # DAQmx Read Code
                DAQmxReadAnalogF64(taskHandle,samples,10.0,DAQmx_Val_GroupByChannel,data,samples*2,byref(read),None)

                #print "Acquired %d points"%read.value
        except DAQError as err:
                print("DAQmx Error: %s"%err)
        finally:
                if taskHandle:
                        # DAQmx Stop Code
                        DAQmxStopTask(taskHandle)
                        DAQmxClearTask(taskHandle)
        val1 = np.mean(data[0:samples])
        val2 = np.mean(data[samples:samples*2 -1])
        return val1, val2

def daqVout(v,chan):                 
        # Declaration of variable passed by reference
        taskHandle = TaskHandle()
        read = int32()

        data = numpy.zeros((1), dtype=numpy.float64)

        for j in range(0,1):
                data[j]= v


        DAQmxCreateTask("",byref(taskHandle))
        DAQmxCreateAOVoltageChan(taskHandle,'Dev1/ao'+str(chan),"",-10.0,10.0,DAQmx_Val_Volts,None)


        ##	/*********************************************/
        ##	// DAQmx Write Code
        ##	/*********************************************/
        DAQmxWriteAnalogF64(taskHandle,1,1,10.0,DAQmx_Val_GroupByChannel,data,None,None)
        ##
        ##	/*********************************************/
        ##	// DAQmx Start Code
        ##	/*********************************************/
        DAQmxStartTask(taskHandle)
        DAQmxStopTask(taskHandle)
        DAQmxClearTask(taskHandle)



def ChangeHVoltage(HVoltage,channel):
        HV = HVoltage
        StartingHV = daqVinAve(channel, 1000, 10.0)
        deltaHV = HV - StartingHV
        if deltaHV == 0:
                pass
        elif deltaHV > 0:
                HVsList = np.arange(StartingHV, HVoltage+0.0005,.025)
        elif deltaHV < 0:
                HVsList = np.arange(StartingHV, HVoltage-0.0005,-.025)
        for i in range(len(HVsList)):
                daqVout(HVsList[i],0)
                time.sleep(0.005)
        daqVout(HV,0)


def ChangeHVoltageSlow(HVoltage,channel):
        HV = HVoltage
        StartingHV = daqVinAve(channel, 1000, 10.0)
        deltaHV = HV - StartingHV
        if deltaHV == 0:
                pass
        elif deltaHV > 0:
                HVsList = np.arange(StartingHV, HVoltage+0.0005,.025)
        elif deltaHV < 0:
                HVsList = np.arange(StartingHV, HVoltage-0.0005,-.025)
        for i in range(len(HVsList)):
                daqVout(HVsList[i],0)
                time.sleep(0.020)
        daqVout(HV,0)

def SweepMeas(samples, totalTime, outRange, inRange, Vout): #single out channel, 8 input channels

    Vouts = np.zeros((samples,), dtype=np.float64)
    for j in range(0,samples,1):
        #print(j)
        Vouts[j] = Vout[0] + j*(Vout[1]-Vout[0])/(samples-1)

    #print("Vouts = ", Vouts)
    
    Vins = np.zeros(((samples+1)*8), dtype=numpy.float64)
    
    outRange0 = outRange

    inRange0 = inRange[0]
    inRange1 = inRange[1]
    inRange2 = inRange[2]
    inRange3 = inRange[3]
    inRange4 = inRange[4]
    inRange5 = inRange[5]
    inRange6 = inRange[6]
    inRange7 = inRange[7]
        
    OtaskHandle = TaskHandle()
    ItaskHandle = TaskHandle()
    read = int32()

    DAQmxCreateTask('',byref(OtaskHandle))
    DAQmxCreateTask('',byref(ItaskHandle))

    DAQmxCreateAOVoltageChan(OtaskHandle,'Dev1/ao'+str(0),'',-1.0*outRange0,1.0*outRange0,DAQmx_Val_Volts,None)

    DAQmxCreateAIVoltageChan(ItaskHandle,'/Dev1/ai' +str(0),'',DAQmx_Val_Cfg_Default,-1.0*inRange0,1.0*inRange0,DAQmx_Val_Volts,None)
    DAQmxCreateAIVoltageChan(ItaskHandle,'/Dev1/ai' +str(1),'',DAQmx_Val_Cfg_Default,-1.0*inRange1,1.0*inRange1,DAQmx_Val_Volts,None)
    DAQmxCreateAIVoltageChan(ItaskHandle,'/Dev1/ai' +str(2),'',DAQmx_Val_Cfg_Default,-1.0*inRange2,1.0*inRange2,DAQmx_Val_Volts,None)
    DAQmxCreateAIVoltageChan(ItaskHandle,'/Dev1/ai' +str(3),'',DAQmx_Val_Cfg_Default,-1.0*inRange3,1.0*inRange3,DAQmx_Val_Volts,None)
    DAQmxCreateAIVoltageChan(ItaskHandle,'/Dev1/ai' +str(4),'',DAQmx_Val_Cfg_Default,-1.0*inRange4,1.0*inRange4,DAQmx_Val_Volts,None)
    DAQmxCreateAIVoltageChan(ItaskHandle,'/Dev1/ai' +str(5),'',DAQmx_Val_Cfg_Default,-1.0*inRange5,1.0*inRange5,DAQmx_Val_Volts,None)
    DAQmxCreateAIVoltageChan(ItaskHandle,'/Dev1/ai' +str(6),'',DAQmx_Val_Cfg_Default,-1.0*inRange6,1.0*inRange6,DAQmx_Val_Volts,None)
    DAQmxCreateAIVoltageChan(ItaskHandle,'/Dev1/ai' +str(7),'',DAQmx_Val_Cfg_Default,-1.0*inRange7,1.0*inRange7,DAQmx_Val_Volts,None)

    DAQmxCfgSampClkTiming(OtaskHandle,'OnboardClock',round(samples/totalTime),DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,samples)
    DAQmxCfgSampClkTiming(ItaskHandle,'OnboardClock',round((samples+1)/totalTime),DAQmx_Val_Falling,DAQmx_Val_FiniteSamps,samples+1) #why falling?

    DAQmxWriteAnalogF64(OtaskHandle,samples,0,10.0,DAQmx_Val_GroupByChannel,Vouts,None,None)

    DAQmxCfgDigEdgeStartTrig(ItaskHandle,'/Dev1/ao/StartTrigger',DAQmx_Val_Rising)

    startTime = time.time()

    DAQmxStartTask(ItaskHandle)
    DAQmxStartTask(OtaskHandle)

    DAQmxReadAnalogF64(ItaskHandle,samples+1,-1,DAQmx_Val_GroupByChannel,Vins,(samples+1)*8,byref(read),None)

    stopTime = time.time()

    DAQmxStopTask(ItaskHandle)
    DAQmxStopTask(OtaskHandle)

    DAQmxClearTask(OtaskHandle)
    DAQmxClearTask(ItaskHandle)

    #print("Vins = ", Vins)
    Vins = np.delete(Vins,np.s_[::samples+1],axis=None)
    
    return startTime, stopTime, Vouts, Vins[0:samples], Vins[samples:samples*2], Vins[samples*2:samples*3], Vins[samples*3:samples*4], Vins[samples*4:samples*5], Vins[samples*5:samples*6], Vins[samples*6:samples*7], Vins[samples*7:samples*8]
   
