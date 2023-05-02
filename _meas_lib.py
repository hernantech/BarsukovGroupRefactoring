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
import scipy as sp
import pytz
import datetime
from scipy.interpolate import interp1d
import pyqtgraph as pg
from PyDAQmx import *
import os
import shutil

fieldCTRL = 3

''' *** GENERAL WRAPPERS *** '''
def printN(q):
    print(q)
    pass
''' *** ---------------- *** '''    

''' *** AUXILLIARY *** '''

def hm():
    country_time_zone = pytz.timezone('America/Los_Angeles')
    country_time = datetime.datetime.now(country_time_zone)
    time_now = country_time.strftime('%H:%M:%S')
    date_today = country_time.strftime('%y-%m-%d')
    return time_now

''' *** ---------------- *** '''    


''' *** COMMUNICATION *** '''

def tme(*arg):
    if arg==():
        n = 2
    else: n = arg[0]
    return round(time.time(),n)

def dte():
    return str(datetime.date.today())

def thisscript():
    return os.path.basename(__file__)

def thisscript_abs():
    return os.path.abspath(__file__)

def makedir(z):
    x = dte() +' '+ z
    y = os.getcwd() + '\\' + x
    if not os.path.exists(y):
        os.makedirs(y)
    savethisscript(y)
    return y

def savethisscript(abspath):
    y = (thisscript()[:-3])+'_'+str(tme())+'.py'
    shutil.copyfile( thisscript() , abspath+'\\'+y )


'''
def openfile_data(absolutepath, name, *args):
    fullname = name + '_{}'.format(tme())
    for item in args:
        fullname += '_{}'.format(str(item))
    fullname += '_.txt'
    y = open(absolutepath + '\\' + fullname , 'wb')
    return y
'''

def openfile_print(absolutepath, *args):
    fullname = arg[0] + '_{}'.format(tme())
    for item in args[1:]:
        fullname += '_{}'.format(str(item))
    fullname += '_.txt'
    y = open(absolutepath + '\\' + fullname , 'wb')
    return y

def savedata(list_of_datalists, fle):
    y = np.transpose( list_of_datalists )
    np.savetxt( fle, y, delimiter='\t', newline='\r\n' )
    fle.close()
    
def save(data, path, *arg):
    fle = openfile_print(path, *arg)
    savedata(data, fle)

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
    print('Could not establish a PUBlisher socket in 10 attempts. ')
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
    print('Could not establish a SUBscriber socket in 10 attempts. ')
    quit()
''' *** ------------- *** '''


''' *** DATA WRAPPERS *** '''

def rnge(x,y,step,signdigits):
    a = abs(step)
    s = np.sign(y-x)
    z = np.arange(x,y,s*a)
    if (abs(y-x)%a) < a*0.01:
        z = np.concatenate((z,[y]))
    for i in range(len(z)): z[i]=round(z[i],signdigits)
    return z

def forwback(x,y,step,signdigits):
    z1 = rnge(x,y,step,signdigits)
    z2 = rnge(y,x,step,signdigits)
    return np.concatenate((z1,z2))
    
def forwback2(x,y,step,fx,fy,finestep,signdigits):
    list1a = rnge(x,fx,step,signdigits)
    list1b = rnge(fx,fy,finestep,signdigits)
    list1c = rnge(fy,y,step,signdigits)
    list2a = rnge(y,fy,step,signdigits)
    list2b = rnge(fy,fx,finestep,signdigits)
    list2c = rnge(fx,x,step,signdigits)
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
    else: print('Could not find the Equipment Object in _meas_lib.py')
    #if typ == 'GPIB::11':
     #   y = GPIB::11(rm, con)
        #print(y.idn())
      #  return y
   # else: print('Could not find the Equipment Object in _meas_lib.py')
   
def eq_v0(eq_list):
    y = []
    y.append( visa.ResourceManager() )
    #res = rm.list_resources()
    for item in eq_list:
        y.append( init_eq(item, eq_list, y[0]) )
    return y[:]

def init_eq(con, eq_list, rm):
    typ = eq_list.get(con)
    
    if typ == 'yoko':
        y = yokogawaGS200(rm, con)
        #print(y.idn())
        return y
    if typ == 'bigmw':
        y = AgilentPSG(rm, con)
        #print(y.idn())
        return y
    if typ == 'nano':
        y = NanoKeysight(rm, con)
        #print(y.idn())
        return y
    if typ == 'gauss':
        y = Gauss(rm, con)
        #print(y.idn())
        return y
    if typ == 'li':
        y = LockIn(rm, con)
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

class yokogawaGS200():
    def __init__(self, rm, con):
        self.confull = precon + str(con)
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
    
class NanoKeysight():
    def __init__(self, rm, con):
        self.con = con
        self.confull = precon + str(con)
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
        self.con = con
        self.confull = precon + str(con)
        self.dev = rm.open_resource(self.confull)
        printN('=LIB=> Initialized: AgilentPSG at '+ str(self.dev.primary_address)+': '+ self.idn())
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
    def f(self,x):
        try:
            q = self.dev.write('freq {}GHz'.format(x))
            print('{} Agilent PSG at {}: Frequency is {}.'.format( hm() , self.con , x))
            return q
        except:
            return False
    '''        
    def f(self,*arg):
        if len(arg) == 0:
            y = float( self.dev.query('freq ?') )
        else:
            f = arg[0]
            if len(arg)>1:
                if arg[1]=='noprint':
                    y = float( self.dev.query('freq ?') )
                else:
                    y = float( self.dev.query('freq ?') )
                    print('{} AgilentPSG at {}: Frequency is set to {}.'.format(tme(),self.con, y))
        return y
    '''        
    def p(self,x):
        try:
            q = self.dev.write('power {}dBm'.format(x))
            return q
        except:
            return False
    def on(self,**arg):
        if 'p' in arg:
            self.p(arg['p'])
        if 'f' in arg:
            self.f(arg['f'])
        self.write('output on')
        y = int(self.query('output?'))
        if int(y) == 1:
            print('{} Agilent PSG at {}: Output is on.'.format( hm() , self.con ))
        else:
            print('{} Agilent PSG at {}: Tried to turn output on, but failed.'.format( hm() , self.con ))
        return
    def off(self):
        self.write('output off')
        print('{} Agilent PSG at {}: Output is turned off.'.format( tme() , self.con ))
        return
    
class Gauss():
    def __init__(self, rm, con):
        self.con = con
        self.confull = precon + str(con)
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

class LockIn():
    def __init__(self,rm, con):
        self.con = con
        self.confull = precon + str(con)
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
    def f(self,*f):
        if f==():
            y = float( self.query('OF.?') )
        else:
            self.write( 'OF.{}'.format(round(f[0], 12 )) )
            y = float( self.query( 'OF.?' ) )
            if abs(y-f[0])>1e-12: 
                print('{} Lock-In at {}: Oscillator frequency attempted at {}, but is {}.'.format( hm(), self.con , f[0] , y ))
            else:
                print('{} Lock-In at {}: Oscillator frequency is set to {}.'.format( hm(), self.con , y ))
        return y
        
    def tc(self,*tc):
        if tc==():
            y = float( self.query('TC.?') )
        else:
            tc_list = [10e-6 , 20e-6, 40e-6, 80e-6, 160e-6, 320e-6, 640e-6, 5e-3, 10e-3, 20e-3, 50e-3, 100e-3, 200e-3, 500e-3, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1e3, 2e3, 5e3, 10e3, 20e3, 50e3, 100e3 ]
            for n in range(len(tc_list)):
                if tc_list[n] > tc[0]:
                    self.write( 'TC{}'.format( n-1 ) )
                    break
            y = float( self.query( 'TC.?' ) )
            if abs(y-tc[0])>0.01*tc[0]: 
                print('{} Lock-In at {}: Time constant attempted at {}, but is {}.'.format( hm(), self.con , tc[0] , y ))
            else:
                print('{} Lock-In at {}: Time constant is set to {}.'.format( hm(), self.con , y ))
        return y
        
    def ac(self, *ac): #Need to complete
        if ac==():
            y = 10*int( self.query('acgain?') )
        else:
            x = round(ac / 10)
            self.write( 'acgain {}'.format( x ) )
            y = int( self.query( 'acgain ?' ) )*10
            if abs(y - ac)>0.01*ac: 
                print('{} Lock-In at {}: AC gain attempted at {}, but is {}.'.format( hm(), self.con , ac , y ))
            else:
                print('{} Lock-In at {}: AC gain is set to {}.'.format( hm(), self.con , y ))
        return y 
        
    def sens(self, *sens):
        if sens==():
            y = float( self.query('sens.?') )
        else:
            sens_list = [2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9, 500e-9, 1e-6, 2e-6, 5e-6, 10e-6, 20e-6, 50e-6,100e-6, 200e-6, 500e-6, 1e-3, 2e-3, 5e-3, 10e-3, 20e-3, 50e-3, 100e-3, 200e-3, 500e-3, 1 ]
            for n in len(sens_list):
                if tc_list[n] > sens:
                    n = n-1
                    self.write( 'sens{}'.format( n+1 ) )
                    break
            y = float( self.query( 'sens.?' ) )
            if abs(y-sens)>0.01*sens: 
                print('{} Lock-In at {}: Sensitivity attempted at {}, but is {}.'.format( hm(), self.con , sens , y ))
            else:
                print('{} Lock-In at {}: Sensitivity is set to {}.'.format( hm(), self.con , y ))
        return y
        
    def osc(self, *osc):
        if osc==():
            y = float( self.query('OA.?') )
        else:
            x = round(osc[0] , 6)
            if x<=1:
                self.write( 'OA.{}'.format( x ) )
                y = float( self.query( 'OA.?' ) )
            else:
                y = float( self.query( 'OA.?' ) )
                print('{} Lock-In at {}: Oscillator amplitude should be <1, nowit is {}. Do it by hand if necessary.'.format( hm(), self.con , y ))
                return y
            print('{} Lock-In at {}: Oscillator amplitude is set to {}.'.format( hm(), self.con , y ))
        return y
            

    def set(self, **setting  ):
        if not setting==():
            for key in setting:
                if key == 'ac': self.ac(setting['ac'])
                if key == 'tc': self.tc(setting['tc'])
                if key == 'osc': self.osc(setting['osc'])
                if key == 'f': self.f(setting['f'])
                if key == 'sens': self.sens(setting['sens'])
        y = {}
        y['tc'] = self.tc()
        y['osc'] = self.osc()
        y['sens'] = self.sens()
        y['ac'] = self.ac()
        y['f'] = self.f()
        return y
        
    def off(self):
        self.osc(0)
        return
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
    
def field_sweep(**arg): #single out channel, 8 input channels+    
    dct = {'init':None , 'wait':1 , 'start':0 , 'end':0 , 'samples':50000 , 'rate':1 , 'outrange':10 , 'inrange':[10,10,10,10,10,10,10,10]}
    dct.update(arg)
    samples = dct['samples']
    wait = dct['wait']
    init = dct['init']
    Vout=[0,0]
    Vout[0] = dct['start']
    Vout[1] = dct['end']
    rate = dct['rate']
    outRange = dct['outrange']
    inRange = dct['inrange']

    
    if not init==None:
        ChangeHVoltage(init,fieldCTRL)
        print('{} Field initialized to {}.'.format(hm(),init))
    time.sleep(wait)
    print('{} Field sweep started.'.format(hm()))
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

    rate_samples = round(samples*(rate/60) / abs(Vout[0]-Vout[1]) )
        
    DAQmxCfgSampClkTiming(OtaskHandle,'OnboardClock',rate_samples,DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,samples)
    DAQmxCfgSampClkTiming(ItaskHandle,'OnboardClock',rate_samples,DAQmx_Val_Falling,DAQmx_Val_FiniteSamps,samples+1) #why falling?

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
    
    return Vouts, Vins[0:samples], Vins[samples:samples*2], Vins[samples*2:samples*3], Vins[samples*3:samples*4], Vins[samples*4:samples*5], Vins[samples*5:samples*6], Vins[samples*6:samples*7], Vins[samples*7:samples*8]
    
