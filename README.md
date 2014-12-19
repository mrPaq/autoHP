autoHP - Automation system to control lights, fans, and pumps for a hydroponic garden.

Purpose - Control lights and pumps by timing events, and fans by sensor events.

Made to run on Linux, and control a Phidget 8/8/8 interface kit (see http://phidgets.com).  This is python-based, but has a RESTful interface by incorporating a Flask server (http://flask.pocoo.org/) accessed by a php-based web interface.  This allows for a rudimentary of current status and provides relay override control.

Currently, I have this running on a Raspberry Pi model B, which controls the phidget via USB, which in turn reads sensor data from the analog inputs, and controls a Sainsmart 8 channel relay board via the 5v digital outputs.  The end result is a bank of 8 independantly controlled 120v sockets.


