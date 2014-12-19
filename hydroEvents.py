#!/usr/bin/python2.7

"""Hydroponic Automation Software

"""

__author__ = 'Paul Paquette'
__version__ = '0.9.1'
__date__ = 'Nov 30 2014'


import sys, os
from threading import Lock, Thread
import threading
import time,logging,signal

from flask import Flask, jsonify, request 

from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs
from Phidgets.Phidget import Phidget 
from Phidgets.Phidget import PhidgetClass
from Phidgets.Manager import Manager
from Phidgets.Devices.InterfaceKit import InterfaceKit

from misc import *
from events import *
from devices import *

app = Flask(__name__)


def display_device_info(manager):
    
    attachedDevices = manager.getAttachedDevices()
    for attachedDevice in attachedDevices:
        output("Found %30s - SN %10d" % (attachedDevice.getDeviceName(), attachedDevice.getSerialNum()))


def display_device_info_verbose(manager):
    attachedDevices = manager.getAttachedDevices()
    output("|------------|----------------------------------|--------------|------------|")
    output("|- Attached -|-              Type              -|- Serial No. -|-  Version -|")
    output("|------------|----------------------------------|--------------|------------|")
    for attachedDevice in attachedDevices:
        output("|- %8s -|- %30s -|- %10d -|- %8d -|" % (attachedDevice.isAttached(), attachedDevice.getDeviceName(), attachedDevice.getSerialNum(), attachedDevice.getDeviceVersion()))
#        output(" %d %d" % (attachedDevice.getDeviceClass(), PhidgetClass.INTERFACEKIT))

    output("|------------|----------------------------------|--------------|------------|")


def setup():
    manager = setup_phidgets()

    devices.load_devices(manager,interfaceKits)
    
    if (os.path.isfile("/tmp/autoHP.reboot")):
        devices.turn_all_off()
        os.remove("/tmp/autoHP.reboot")

    return manager


## Event Handler Callback Functions ###################################

def ManagerDeviceAttached(e):
    attached = e.device
    logging.info("Manager - Device %i: %s Attached!" % (attached.getSerialNum(), attached.getDeviceName()))

def ManagerDeviceDetached(e):
    detached = e.device
    logging.warning("Manager - Device %i: %s Detached!" % (detached.getSerialNum(), detached.getDeviceName()))

def ManagerError(e):
    logging.error("Manager Phidget Error %i: %s" % (e.eCode, e.description))


## Interface Kit handlers ########################################
def interfaceKitAttached(e):
    attached = e.device
    output("InterfaceKit %i Attached!" % (attached.getSerialNum()))

def interfaceKitDetached(e):
    detached = e.device
    output("InterfaceKit %i Detached!" % (detached.getSerialNum()))

def interfaceKitError(e):
    try:
        source = e.device
        output("InterfaceKit %i: Phidget Error %i: %s" % (source.getSerialNum(), e.eCode, e.description))
    except PhidgetException as e:
        output("Phidget Exception %i: %s" % (e.code, e.details))



## Phidget Stuff ######################################################

def close_phidgets(manager):
    try:
        manager.closeManager()
    except PhidgetException as e:
        output("Phidget Exception %i: %s" % (e.code, e.details))
        logging.error("Phidget Exception %i: %s" % (e.code, e.details))
        output("Exiting....")
        logging.error("Exiting....")
        exit(1)


def setup_phidgets():
    global interfaceKits
    interfaceKits = InterfaceKits()

    "Print Creating phidget manager"
    try:
        manager = Manager()
    except RuntimeError as e:
        output("Runtime Exception: %s" % e.details)
        output("Exiting....")
        exit(1)

    try:
        manager.setOnAttachHandler(ManagerDeviceAttached)
        manager.setOnDetachHandler(ManagerDeviceDetached)
        manager.setOnErrorHandler(ManagerError)
    except PhidgetException as e:
        output("Phidget Exception %i: %s" % (e.code, e.details))
        output("Exiting....")
        exit(1)

    output("Opening phidget manager....")
    logging.info("Opening phidget manager....")

    try:
        manager.openManager()
        #manager.openRemote("hydropi","hydropi")
    except PhidgetException as e:
        output("Phidget Exception %i: %s" % (e.code, e.details))
        logging.error("Phidget Exception %i: %s" % (e.code, e.details))
        output("Exiting....")
        logging.error("Exiting....")
        exit(1)

    # Wait a moment for devices to attache......
    output("\nWaiting one sec for devices to attach....\n\n")
    logging.info("Waiting one sec for devices to attach....")
    time.sleep(1)

    output("Phidget manager opened.")

    attachedDevices = manager.getAttachedDevices()
    for attachedDevice in attachedDevices:
     
        output("Found %30s - SN %10d" % (attachedDevice.getDeviceName(), attachedDevice.getSerialNum()))
        if attachedDevice.getDeviceClass() == PhidgetClass.INTERFACEKIT:
            output("  %s/%d is an InterfaceKit" % ( attachedDevice.getDeviceName(),attachedDevice.getSerialNum()))
            #Create an interfacekit object
            try:
                newInterfaceKit = InterfaceKit()
            except RuntimeError as e:
                output("Runtime Exception: %s" % e.details)
                output("Exiting....")
                exit(1)

            output("  Opening...")
            try:
                newInterfaceKit.openPhidget()
            except PhidgetException as e:
                output("Phidget Exception %i: %s" % (e.code, e.details))
                output("Exiting....")

            output("  Setting handlers...")
            try:
                newInterfaceKit.setOnAttachHandler(interfaceKitAttached)
                newInterfaceKit.setOnDetachHandler(interfaceKitDetached)
                newInterfaceKit.setOnErrorhandler(interfaceKitError)
            except PhidgetException as e:
                output("Phidget Exception %i: %s" % (e.code, e.details))
                output("Exiting....")
                exit(1)

            output("  Attaching...")
            try:
                newInterfaceKit.waitForAttach(5000)
            except PhidgetException as e:
                output("Phidget Exception %i: %s" % (e.code, e.details))
                try:
                    newInterfaceKit.closePhidget()
                except PhidgetException as e:
                    output("Phidget Exception %i: %s" % (e.code, e.details))
                    output("Exiting....")
                    exit(1)
                output("Exiting....")
                exit(1)

            output("  Setting the data rate for each sensor index to 1000ms....")
            for i in range(newInterfaceKit.getSensorCount()):
                try:
                    newInterfaceKit.setDataRate(i, 1000)
                except PhidgetException as e:
                    output("Phidget Exception %i: %s" % (e.code, e.details))

            interfaceKits.kitList.append(newInterfaceKit)
            
        
    display_device_info(manager)
    return manager 

## Flask stuff ########################################################

@app.route('/api/status', methods=['GET'])
def get_status():
    zones = []
    tmpDevices = []
    time.sleep(0.1)

    lock = threading.Lock();

    with lock:
        for curDev in devices.deviceList:
            tDict =({'deviceID':curDev.deviceID,
                            'zoneID':curDev.zoneID,
                            'devType':curDev.devType})
            if curDev.devType == "Sensor":
                tDict.update({'rawValue':curDev.get_raw_value(),
                                   'value':curDev.get_value()})
            if curDev.devType == "Relay":
                tDict.update({'curState': "On" if curDev.get_state() else "Off",
                                   'override': "manual" if curDev.override else "auto" })
            tmpDevices.append(tDict)
    
    deviceData = {'devices':tmpDevices}

    return jsonify(deviceData)

@app.route('/api/override', methods=['POST'])
def set_override():
#    for value in request.form:
#        logging.error(value)
#        logging.error(request.form[value])
    if ( request.form['action'] == "manual"):
        lock = threading.Lock();
        with lock:
            try:
                devices.set_device_override(request.form['deviceID'],True)
            except:
                pass
    else:
        lock = threading.Lock();
        with lock:
             try:
                 devices.set_device_override(request.form['deviceID'],False)
             except:
                 pass
   
    return ""

@app.route('/api/manual', methods=['POST'])
def set_state():
#    for value in request.form:
#        logging.error(value)
#        logging.error(request.form[value])
    if devices.get_device_override(request.form['deviceID']) :
        if ( request.form['action'] == "On"):
            lock = threading.Lock();
            with lock:
                devices.set_device_state(request.form['deviceID'],True)
        elif ( request.form['action'] == "Off"):
            lock = threading.Lock();
            with lock:
                devices.set_device_state(request.form['deviceID'],False)
   
    return ""

def start_flask():
    output("Starting Flask thread...")
    flaskThread = threading.Thread(target=app.run)
    flaskThread.setDaemon(True)
    flaskThread.start()

       
## Main Program #######################################################

logFileName = "phidget.log"



def main():
    global devices
    defaultDir="/etc/autoHP"
    logging.basicConfig(filename=defaultDir+"/"+logFileName)

    devices=Devices(defaultDir)

    manager = setup()

    ## Send Flask off on its own #####################################
    start_flask()

    ## Main Processing loop ###########################################
    lastSec=60
    while True:
        try:
            ## Start main work here ##############
            time.sleep(1)
            myTime = time.gmtime()
            curSec=int(myTime[5])
            if curSec <= lastSec:
                lastSec=curSec
                output(time.strftime("%H:%M") + " Check Events...")
                newEvents = Events()
                newEvents.load_events(defaultDir,devices)
                newEvents.process()


        except KeyboardInterrupt:
            output("Interrupted - leaving...")
            break

    ## Received an end somewhere ######################################
    output("Closing...")
    close_phidgets(manager)

    output("Done.")
    logging.info("Done.")

if __name__ == '__main__':
    main()
