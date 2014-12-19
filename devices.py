#!/usr/bin/python

"""device stuff for
Hydroponic Automation Software

"""

__author__ = 'Paul Paquette'
__version__ = '0.0.1'
__date__ = 'Nov 11 2014'


import sys, thread
#from threading import Lock Thread
import threading
import time,logging,signal
from misc import *
import math

from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs
from Phidgets.Phidget import Phidget 
from Phidgets.Phidget import PhidgetClass
from Phidgets.Manager import Manager
from Phidgets.Devices.InterfaceKit import InterfaceKit

class Devices:
    def __init__(self,inDefaultDir):
        self.defaultDir = inDefaultDir;
        self.deviceList = []

    def create_device_by_text(self,attachedDevices,interfaceKits,inDatLine,fields):
        foundPhidget = None
        for attachedDevice in attachedDevices:
            if attachedDevice.getSerialNum() == int(fields[2]):
                foundPhidget = attachedDevice
                break
        if foundPhidget == None:
            sys.exit('Couldn\'t find phidget for device %s SN %s' % (fields[0],fields[2]))
        tmpInterFaceKit=None
        for curInterfaceKit in interfaceKits.kitList:
            if curInterfaceKit.getSerialNum() == int(fields[2]):
                tmpInterFaceKit=curInterfaceKit
                break
        if tmpInterFaceKit == None:
            sys.exit('Interface Kit not found for device:\n%s' %(inDatLine))
        
        if fields[3] == "DO":
            tmpDevice = Relay(fields[0],fields[1],fields[5],fields[7],foundPhidget,fields[2])
        elif fields[3] == "AI":
            if fields[4].lower() == 'cur25a':
                tmpDevice = Cur25Sensor(fields[0],fields[1],fields[5],foundPhidget,fields[2])
            elif fields[4].lower() == 'lux70k':
                try: 
                    tmpDevice = LuxSensor(fields[0],fields[1],fields[5],foundPhidget,fields[2],fields[8],fields[9])
                except IndexError:
                    sys.exit('Error reading phidgets.dat , line:\n%s' % (inDatLine))
            elif fields[4].lower() == 'humid':
                tmpDevice = HumiditySensor(fields[0],fields[1],fields[5],foundPhidget,fields[2])
            elif fields[4].lower() == 'temp':
                tmpDevice = TempSensor(fields[0],fields[1],fields[5],foundPhidget,fields[2])
            else:
                tmpDevice = Sensor(fields[0],fields[1],fields[5],foundPhidget,fields[2])
        tmpDevice.assign_interfacekit(curInterfaceKit)
        return tmpDevice
        

    def get_device(self,inDeviceID):
        for curDevice in self.deviceList:
            if curDevice.deviceID == inDeviceID:
                return curDevice
        print "Get Device - Device " + inDeviceID + " not found"
        return False
 
#    def get_device_last_state(self,inDeviceID):
#        for curDevice in self.deviceList:
#            if curDevice.deviceID == inDeviceID:
#                return curDevice.lastState

    def get_device_override(self,inDeviceID):
        for curDevice in self.deviceList:
            if curDevice.deviceID == inDeviceID:
                return curDevice.is_override()
        print "Device override - Device " + inDeviceID + " not found"
        return False

#    def get_device_state(self,inDeviceID):
#        for curDevice in self.deviceList:
#            if curDevice.deviceID == inDeviceID:
#                return curDevice.get_state()
 
    def is_override(self,inDeviceID):
        for curDevice in self.deviceList:
            if curDevice.deviceID == inDeviceID:
                return curDevice.is_override()
        print "Device override - Device " + inDeviceID + " not found"
        return False

    def load_devices(self,manager,interfaceKits):
        attachedDevices = manager.getAttachedDevices()
        print("Reading device list...")

        try:
            csvfile = open(self.defaultDir+"/"+'devices.dat','r')
            for curLine in csvfile:  
                curLine = space_cleanup(curLine)
                fields=curLine.split(",")
                try:
                    fields[0].index("#")
                except:
                    tmpDevice=self.create_device_by_text(attachedDevices,interfaceKits,curLine,fields)

#                    for curInterfaceKit in interfaceKits.kitList:
#                        if curInterfaceKit.getSerialNum() == int(fields[2]):
#                            tmpDevice.assign_interfacekit(curInterfaceKit)
#                            break
                    self.deviceList.append(tmpDevice)
        
                    newZone=add_zone(fields[1])
                    newZone.add_device(tmpDevice)
                    
        except IOError as e:
            sys.exit('Error reading phidgets.dat , line %d: %s' % (csvfile.line_num, e))
            logging.error('Error reading phidgets.dat , line %d: %s' % (csvfile.line_num, e))
        csvfile.close()

    def set_device_override(self,inDeviceID,inValue):
        try:
            curDevice=self.get_device(inDeviceID)
            curDevice.set_override(inValue)
        except:
            pass 

    def set_device_state(self,inDeviceID,inValue):

        try:
            curDevice=self.get_device(inDeviceID)
            curDevice.set_state(inValue)
        except:
            pass 

    def turn_all_off(self):
        for curDevice in self.deviceList:
            if curDevice.devType.lower() == 'relay':
                curDevice.set_state(0)

class Device:
    def __init__(self, inDeviceID,inZoneID,inDevType,inPort,inParent,inParentSN):
        self.deviceID = inDeviceID
        self.zoneID = inZoneID
        self.devType = inDevType
        self.port = inPort
        self.parent = inParent
        self.parentSN = inParentSN
        self.override = False
        self.interfaceKit = None

    def assign_interfacekit(self,inInterfaceKit):
        self.interfaceKit = inInterfaceKit
 
    def is_override(self):
        return self.override

class Sensor(Device):
    def __init__(self, inSensorID,inZoneID,inPort,inParent,inParentSN):
        Device.__init__(self,inSensorID,inZoneID,"Sensor",inPort,inParent,inParentSN)

#    def get_state(self):
#        curState=self.interfaceKit.getSensorValue(int(self.port))
#        return curState

    def get_raw_value(self):
        if self.interfaceKit.isAttached():
            rawValue=self.interfaceKit.getSensorValue(int(self.port))
            return rawValue
        else:
            return 0

    def get_value(self):
        return self.get_raw_value()


class HumiditySensor(Sensor):
    def __init__(self, inSensorID,inZoneID,inPort,inParent,inParentSN):
        Sensor.__init__(self,inSensorID,inZoneID,inPort,inParent,inParentSN)

    def convert_raw(self,inValue):
        return ( inValue * 0.1906 ) - 40.2

    def get_value(self):
        return self.convert_raw(self.get_raw_value())
        

class Cur25Sensor(Sensor):
    def __init__(self, inSensorID,inZoneID,inPort,inParent,inParentSN):
        Sensor.__init__(self,inSensorID,inZoneID,inPort,inParent,inParentSN)

    def convert_raw(self,inValue):
        return inValue/40 * 115

    def get_value(self):
        return self.convert_raw(self.get_raw_value())


class LuxSensor(Sensor):
    def __init__(self, inSensorID,inZoneID,inPort,inParent,inParentSN,inM,inB):
        Sensor.__init__(self,inSensorID,inZoneID,inPort,inParent,inParentSN)
        self.m = float(inM)
        self.b = float(inB)

    def convert_raw(self,inValue):
        return math.pow(2.71828,self.m * float(inValue) + self.b)

    def get_value(self):
        return self.convert_raw(self.get_raw_value())
        

class TempSensor(Sensor):
    def __init__(self, inSensorID,inZoneID,inPort,inParent,inParentSN):
        Sensor.__init__(self,inSensorID,inZoneID,inPort,inParent,inParentSN)

    def convert_raw(self,inValue):
        return ( inValue * 0.22222 ) - 61.11

    def get_value(self):
        return self.convert_raw(self.get_raw_value())
        

class Relay(Device):
    def __init__(self, inRelayID,inZoneID,inPort,inDefVal,inParent,inParentSN):
        Device.__init__(self,inRelayID,inZoneID,"Relay",inPort,inParent,inParentSN)
        self.defVal = inDefVal
        self.lastState = 0

    def get_last_state(self):
        return self.lastState

    def get_state(self):
        if self.interfaceKit.isAttached():
            curState=not self.interfaceKit.getOutputState(int(self.port))
            return curState
        else:
            return None
   
        

    def set_override(self,inValue):
        self.override=inValue
#        logging.error("override hit")


    def set_state(self,inValue):
        if self.interfaceKit.isAttached():
            self.lastState = inValue
            self.interfaceKit.setOutputState(int(self.port),not inValue)

class Zone:
    def __init__(self, inZoneID):
        self.zoneID = inZoneID
        self.deviceList = []

    def add_device(self,inDevice):
        self.deviceList.append(inDevice)


def add_zone(inZoneID):
    zoneHit = False    
    for tmpZone in zoneList:
        if ( tmpZone.zoneID == inZoneID ):
             zoneHit = True
             curZone = tmpZone
             break

    if ( zoneHit == False ):
        curZone=Zone(inZoneID)
        zoneList.append(curZone)

    return curZone
 
class InterfaceKits:
    def __init__(self):
        self.kitList = []

   
