AirPi
========

A Raspberry Pi weather station and air quality monitor.

This is the code for the project located at http://airpi.es

Currently it is split into airpi.py, as well as multiple input and multiple output plugins. airpi.py collects data from each of the input plugins specified in sensors.cfg, and then passes the data provided by them to each output defined in outputs.cfg. The code for each sensor plugin is contained in the 'sensors' folder and the code for each output plugin in the 'outputs' folder.

Some of the files are based off code for the Raspberry Pi written by Adafruit: https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code

For installation instructions, see http://airpi.es/kit.php

## Installation

### Prerequisites

You will need to install the following dependencies:

`sudo apt-get install git-core python-dev python-pip python-smbus libxml2-dev libxslt1-dev python-lxml i2c-tools`

and

`sudo pip install rpi.gpio requests`

AirPi requires python-eeml.  To install:

```
cd ~/git
git clone https://github.com/petervizi/python-eeml.git
cd python-eeml
sudo python setup.py install
```

### i2c

To set up i2c, first add your user to the i2c group.  For example, if your username is "pi":

`sudo adduser pi i2c`

Now, add the modules needed.

`sudo nano /etc/modules`

Add the following two lines to the end of the file:

```
i2c-bcm2708
i2c-dev
```

Exit by pressing CTRL+X, followed by y to confirm you want to save, and ⏎ (enter) to confirm the filename.

Finally, unblacklist i2c by running the following command:

`sudo nano /etc/modprobe.d/raspi-blacklist.conf`

Add a `#` character  at the beginning of the line `blacklist i2c-bcm2708`. Then exit in the same way as last time.

Now, reboot your Raspberry Pi:

`sudo reboot`

### Board Version

Let's check to see which board version you have.  Run:

`sudo i2cdetect -y 0`

You should see this as the output:

```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- 77
```

If not, run:

`sudo i2cdetect -y 1`

and you should see the above.  This tells you if your board is version 0 or 1.  This is important for the next step.

### Get The AirPi Code

Clone this repo into your git directory (or wherever you want):

```
cd ~/git
git clone https://github.com/tomhartley/AirPi.git
cd AirPi
```

### Configuring

Edit the settings file by running:

`nano sensors.cfg`

The start of the file should look like this:

```
[BMP085-temp]
filename=bmp085
enabled=on
measurement=temp
i2cbus = 1

[BMP085-pres]
filename=bmp085
enabled=on
measurement=pres
mslp=on
i2cbus = 1
altitude=40
```

If your board version is "0" change both instances of `i2cbus = 1` to `i2cbus = 1`

Press CTRL+X to exit the file, when prompted, press "y" to save the file.

If you want to push the data to Xively, edit the `outputs.cfg` file:

`nano outputs.cfg`

The start of the file should look like this:

```
[Print]
filename=print
enabled=on

[Xively]
filename=xively
enabled=on
APIKey=xxxxxxxxxx
FeedID=xxxxxxxxxx
```

If you have registered with https://xively.com - you can add your API Key and Feed ID here.

## Running

AirPi **must** be run as root.

`sudo python airpi.py`

If everything is working, you should see output similar to this:

```
Success: Loaded sensor plugin BMP085-temp
Success: Loaded sensor plugin BMP085-pres
Success: Loaded sensor plugin MCP3008
Success: Loaded sensor plugin DHT22
Success: Loaded sensor plugin LDR
Success: Loaded sensor plugin MiCS-2710
Success: Loaded sensor plugin MiCS-5525
Success: Loaded sensor plugin Mic
Success: Loaded output plugin Print
Success: Loaded output plugin Xively

Time: 2014-06-04 09:10:18.942625
Temperature: 30.2 C
Pressure: 992.55 hPa
Relative_Humidity: 35.9000015259 %
Light_Level: 3149.10025707 Ohms
Nitrogen_Dioxide: 9085.82089552 Ohms
Carbon_Monoxide: 389473.684211 Ohms
Volume: 338.709677419 mV
Uploaded successfully

```
