#autoHP
##Automation system to control lights, fans, and pumps for a hydroponic garden.

Made to run on Linux, and control a Phidget 8/8/8 interface kit (see http://phidgets.com).  This is python-based, but has a RESTful interface by incorporating a Flask server (http://flask.pocoo.org/) accessed by a php-based web interface.  This allows for a rudimentary view of current status and provides relay override control.

Currently, I have this running on a Raspberry Pi model B, which controls the phidget via USB, which in turn reads sensor data from the analog inputs, and controls a Sainsmart 8 channel relay board via the 5v digital outputs.  The end result is a bank of 8 independantly controlled 120v sockets.

Sorry for any missing bits of information - This documentation is a work in progress (and so is the program).

**See Wiki for more detailed information**

**Next:** need to add recording of sensor data & relay status to a database.

**Problem:** in recording of data, and trying to stay with an IOT point of view, I would like to change the RESTful/Flask HTML system to a CoAP system.  This in turn means I need a CoAP-capable PHP interface, which it doesn't look like it exists.
To that end, I'm working on building a very rudimentary CoAP extension for PHP based on Olaf Bergmann's libcoap and his simple client example (see http://sourceforge.net/projects/libcoap/).  Looks like this will take some time...

###Requirements###
(this is a work in progress - will need to reinstall from scratch to get proper requirements)
- Linux on somthing with an available USB port (CentOS and Raspbian work)
- Python 2.7.6
- Flask

If you want the web-interface then:
- Webserver (assume apache2+)
- php 5.?

Startup by adding the following to /etc/rc.local
```
# test for restart events...
touch /tmp/autoHP.rebootA
# Start event system...
/root/autoHP/autoHP.py >> /var/log/autoHP.log 2>&1 &
```

I'm assuming the program is run from folder /root/autoHP/ (I know, not a good idea, but I'll work on an install script to proper locations soon).
Currently assumes the .dat files are in /etc/autoHP/

