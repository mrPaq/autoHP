
""" Event classes for...
Hydroponic Automation Software
"""

__author__ = 'Paul Paquette'
__version__ = '0.0.2'
__date__ = 'Nov 20 2014'


from misc import *
#from time import *
from datetime import *

class TimeETypes:
    Single, OnWindow, RepWindow = range(3)

class Events:
    def __init__(self):
        self.eventList = []

    def load_events(self,inDir,inDevices):
        print("Loading Events...")
        try:
            csvfile = open(inDir + '/' +'events.dat','r')
            for curLine in csvfile:
                curLine = space_cleanup(curLine)
                fields=curLine.split(",")
                try:
                    fields[0].index("#")
                except:
                    if fields[0].lower() == "time":
                        event = TimeEvent.create_event_from_fields(fields,inDevices)
                    elif fields[0].lower() == "sensor":
                        event = SensorEvent.create_event_from_fields(fields,inDevices)
                    else:
                        output("Event type not found")
                        output(fields)
                        event = False

                    if event != False:
                        self.eventList.append(event)

        except IOError as e:
            sys.exit('Error reading events.dat , line %d: %s' % (csvfile.line_num, e))
            logging.error('Error reading phidgets.dat , line %d: %s' % (csvfile.line_num, e))
        
    def process(self,**kwargs):
        curTime = datetime.combine(date.fromtimestamp(0),datetime.now().time());
        
        for key, value in kwargs.iteritems():
            if key.lower() == "datetime":
                curTime=value
            elif key.lower() == "str":
                curTime = datetime.strptime(value,"%H:%M")

        for event in self.eventList:
            event.process(datetime=curTime)


class TimeEvent(object):
    def __init__(self, inDevice, inInitTime):
        self.device = inDevice
        self.initTime = datetime.combine(date.fromtimestamp(0),datetime.strptime(inInitTime,"%H:%M").time())

    @staticmethod
    def create_event_from_fields(inFields,inDevices):    
        eventDevice = inDevices.get_device(inFields[2])
        if not eventDevice:
            output("Error creating TimeEvent, couldn't find device")
            output(inFields)
            return False
        elif inFields[1].lower() == "onwindow":
            return WindowTimeEvent.create_event_from_fields(inFields,inDevices)
        elif inFields[1].lower() == "repwindow":
            return RepWindowTimeEvent.create_event_from_fields(inFields,inDevices)

    def convert_to_min(self,inLength):
        if isinstance( inLength, int ) and inlength > 0: 
            return int(inLength)
        timeunit=inLength.lower()[-1:]
        if timeunit == "h":
            minuteLength=60*int(inLength[:-1])
        elif timeunit == "m":
            minuteLength = int(inLength[:-1])
        else:
            raise MyException("Invalid timelength passed.")
        return minuteLength
        
    def get_start_time_str(self):
        return self.initTime.strftime("%H:%M")

#class SingleTimeEvent(TimeEvent):
#    def __init__(self,inDevice,inEventTime):
#        TimeEvent.__init__(self,inDevice,inEventTime)
#        
#    def create_event_from_fields(self,inFields,inDevices):    

class WindowTimeEvent(TimeEvent):
    def __init__(self,inDevice,inEventTime,inRunLength):
        TimeEvent.__init__(self,inDevice,inEventTime)
        self.runLength = timedelta(minutes=self.convert_to_min(inRunLength))

    @staticmethod
    def create_event_from_fields(inFields,inDevices):    
        eventDevice = inDevices.get_device(inFields[2])
        if eventDevice:
            return WindowTimeEvent(eventDevice,inFields[4],inFields[5])
        else:
            output("Error creating WindowTimeEvent, couldn't find devices")
            output(inFields)
            return False
                     
    def get_end_time_str(self):
        tmpTime = self.initTime + self.runLength
        return tmpTime.strftime("%H:%M")

    def get_state(self,**kwargs):
        curTime = datetime.combine(date.fromtimestamp(0),datetime.now().time());
        
        for key, value in kwargs.iteritems():
            if key.lower() == "datetime":
                curTime=value
            elif key.lower() == "str":
                curTime = datetime.strptime(value,"%H:%M")
            
        endTime = self.initTime + self.runLength
        if endTime.date() > curTime.date():
            'Perform cross-day check'
            if self.initTime <= curTime or \
               (curTime + timedelta(days=1)) <= endTime:
               return True
            else:
               return False 

        else:
            if self.initTime <= curTime and \
                endTime >= curTime:
                return True
            else:
                return False

    def process(self,**kwargs):
        curTime = datetime.combine(date.fromtimestamp(0),datetime.now().time());
        
        for key, value in kwargs.iteritems():
            if key.lower() == "datetime":
                curTime=value
            elif key.lower() == "str":
                curTime = datetime.strptime(value,"%H:%M")

        try:
            curState=self.device.get_state()
                        
            if self.device.is_override():
                if curState != \
                    self.device.get_last_state():
                    self.device.set_state(self.device.get_last_state())
            else:
                shouldBe = self.get_state();
                if shouldBe != curState:
                    if shouldBe:
                        output(self.device.deviceID + ": setting state on")
                        self.device.set_state(True)
                    else:
                        output(self.device.deviceID + ": setting state off")
                        self.device.set_state(False)
                            
            if self.get_state():
                eventStatus = "On" 
            else:
                eventStatus = "Off"

            if self.device.is_override():
                override = "Manual"
            else:
                override = "Automatic"

            realState = "On" if curState else "Off"
            output(self.__class__.__name__ + "|" + self.device.deviceID + \
                        "|" + self.get_start_time_str() + "|" + \
                        self.get_end_time_str() + "|" + eventStatus + \
                        "|" + realState + "|" + override)
        except:
            pass



class RepWindowTimeEvent(WindowTimeEvent):
    def __init__(self,inDevice,inEventTime,inRunLength,
                 inOnMin,inOffMin):
        WindowTimeEvent.__init__(self,inDevice,inEventTime,inRunLength)
        self.onMin= timedelta(minutes=self.convert_to_min(inOnMin))
        self.offMin=timedelta(minutes=self.convert_to_min(inOffMin))
        self.maxCycleLength=self.onMin + self.offMin
        
    @staticmethod
    def create_event_from_fields(inFields,inDevices):    
        eventDevice = inDevices.get_device(inFields[2])
        if eventDevice:
            return RepWindowTimeEvent(eventDevice,inFields[4],inFields[5],
                                      inFields[6],inFields[7])
        else:
            output("Error creating RepWindowTimeEvent, couldn't find devices")
            output(inFields)
            return False
        

    def get_state(self,**kwargs):
        #curTime = datetime.now();
        curTime = datetime.combine(date.fromtimestamp(0),datetime.now().time());
        
        for key, value in kwargs.iteritems():
            if key.lower() == "datetime":
                curTime=value
            elif key.lower() == "str":
                curTime = datetime.strptime(value,"%H:%M")

        # check for cross day event
        endTime = self.initTime + self.runLength
        if endTime.date() > curTime.date() and \
            self.initTime > curTime: 
            curTime=curTime + timedelta(days=1)

        if super(RepWindowTimeEvent,self).get_state(datetime=curTime):
            testTime = timedelta(days=0);
            while super(RepWindowTimeEvent, self).get_state(datetime=(self.initTime + testTime)):

                if self.initTime + testTime + self.onMin < curTime:
                    testTime = testTime + self.maxCycleLength
                elif self.initTime + testTime <= curTime:
                    return True
                else:
                    return False
                    
        return False           
            



###############################################################

class SensorEvent():
    def __init__(self,inSenseDevice,inTestValue,inActivateDevice,inActValue):
        self.device = inSenseDevice
        self.testValue = inTestValue
        self.activateDevice = inActivateDevice
        self.actValue = inActValue

    def act(self):
        if self.actValue.lower() == "on":
            shouldBe = True
        elif self.actValue.lower() == "off":
            shouldBe = False
        else:
            shouldBe = self.actValue

        curState = self.activateDevice.get_state()
        if shouldBe != curState:
            self.activateDevice.set_state(shouldBe)
            output(self.activateDevice.deviceID + \
                ": setting state " + self.actValue)
                

    @staticmethod
    def create_event_from_fields(inFields,inDevices):    
        if inFields[1] == 'lt':
            return ltSensorEvent.create_event_from_fields(inFields,inDevices)
        if inFields[1] == 'ge':
            return geSensorEvent.create_event_from_fields(inFields,inDevices)
     
    def print_info(self):
        if self.test():
            eventStatus = "On"
        else:
            eventStatus = "Off"

        if self.activateDevice.get_state():
            actual = "On"
        else:
            actual = "Off"

        if self.activateDevice.is_override():
            override = "Manual"
        else:
            override = "Automatic"
        curTest = ( "%.2f" % (self.device.get_value() ))

        output(self.__class__.__name__ + "|" + self.device.deviceID + \
                        "|" + self.testValue + "|" + \
                        self.activateDevice.deviceID + "|" + \
                        curTest + "|" + self.actValue + \
                        "|" + actual + "|" + override)



class ltSensorEvent(SensorEvent):
    def __init__(self,inSenseDevice,inTestValue,inActivateDevice,inActValue):
        SensorEvent.__init__(self,inSenseDevice,
                             inTestValue,inActivateDevice,
                             inActValue)

    @staticmethod
    def create_event_from_fields(inFields,inDevices):    
        senseDevice = inDevices.get_device(inFields[2])
        activateDevice = inDevices.get_device(inFields[4])
        if senseDevice and activateDevice:
            return ltSensorEvent(senseDevice,inFields[3],
                                 activateDevice,inFields[5])
        else:
            output("Error creating ltSensorEvent, couldn't find devices")
            output(inFields)
            return False

    def test(self):
        return self.device.get_value() < float(self.testValue)

    def process(self,**kwargs):
        if self.activateDevice.is_override():
            if self.activateDevice.get_state() != \
                self.activateDevice.get_last_state():
                self.activateDevice.set_state(self.activateDevice.get_last_state())
        else:
            self.act() if self.test() else None

        self.print_info()
     
        
class geSensorEvent(SensorEvent):
    def __init__(self,inSenseDevice,inTestValue,inActivateDevice,inActValue):
        SensorEvent.__init__(self,inSenseDevice,
                             inTestValue,inActivateDevice,
                             inActValue)

    @staticmethod
    def create_event_from_fields(inFields,inDevices):    
        senseDevice = inDevices.get_device(inFields[2])
        activateDevice = inDevices.get_device(inFields[4])
        if senseDevice and activateDevice:
            return geSensorEvent(senseDevice,inFields[3],
                                 activateDevice,inFields[5])
        else:
            output("Error creating geSensorEvent, couldn't find devices")
            output(inFields)
            return False

    def test(self):
        return self.device.get_value() >= float(self.testValue)

    def process(self,**kwargs):
        if self.activateDevice.is_override():
            if self.activateDevice.get_state() != \
                self.activateDevice.get_last_state():
                self.activateDevice.set_state(self.activateDevice.get_last_state())
        else:
            self.act() if self.test() else None

        self.print_info()
     


    

        
        
        

    

        
        
        
        
        

    

        
        
        
