autoHP - Automation system to control lights, fans, and pumps for a hydroponic garden.

Purpose - Control lights and pumps by timing events, and fans by sensor events.

Made to run on Linux, and control a Phidget 8/8/8 interface kit (see http://phidgets.com).  This is python-based, but has a RESTful interface by incorporating a Flask server (http://flask.pocoo.org/) accessed by a php-based web interface.  This allows for a rudimentary view of current status and provides relay override control.

Currently, I have this running on a Raspberry Pi model B, which controls the phidget via USB, which in turn reads sensor data from the analog inputs, and controls a Sainsmart 8 channel relay board via the 5v digital outputs.  The end result is a bank of 8 independantly controlled 120v sockets.

Next: need to add recording of sensor data & relay status to a database.
Problem: in recording of data, and trying to stay with an IOT point of view, I would like to change the RESTful/Flask HTML system to a CoAP system.  This in turn means I need a CoAP-capable PHP interface, which it doesn't look like it exists.
To that end, I'm working on building a very rudimentary CoAP extension for PHP based on Olaf Bergmann's libcoap and the simple client example (see http://sourceforge.net/projects/libcoap/).  Looks like this will take some time...

Startup by adding the following to /etc/rc.local
# test for restart events...
touch /tmp/autoHP.rebootA
# Start event system...
/root/autoHP/autoHP.py >> /var/log/autoHP.log 2>&1 &


