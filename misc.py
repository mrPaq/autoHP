
"""Misc stuff for
Hydroponic Automation Software

"""

__author__ = 'Paul Paquette'
__version__ = '0.0.1'
__date__ = 'Nov 11 2014'

import sys

global manager

global deviceList
deviceList = []

global zoneList
zoneList = []

class MyException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

def space_cleanup(inStr):
    inStr=inStr.replace("  "," ")
    inStr=inStr.replace(", ",",")
    inStr=inStr.replace("\n","")
    return inStr.replace(" ,",",")

def output(inStr):
    sys.stdout.write(inStr + "\n")
    sys.stdout.flush()

