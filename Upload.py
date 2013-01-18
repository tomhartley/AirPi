#!/usr/bin/python

import time
import datetime
import eeml
import RPi.GPIO as GPIO
from interfaces.DHT22 import DHT22
from interfaces.BMP085 import BMP085
from interfaces.MCP3008 import MCP3008, AQSensor, LightSensor, MiCS2710

DEBUG = 1
LOGGER = 1


DHTPin = 4

GPIO.setmode(GPIO.BCM)
GPIO.setup(22,GPIO.OUT)
GPIO.setup(21,GPIO.OUT)

BMP085Address = 0x77

SPIMOSI = 23
SPIMISO = 24
SPICLK = 18
SPICS = 25

AQADC = 1
LightADC = 0
MiCSADC = 2

dht = DHT22.DHT22(DHTPin)
bmp = BMP085.BMP085()
adc = MCP3008.MCP3008(SPIMOSI,SPIMISO,SPICLK,SPICS)
airSensor = AQSensor.AQSensor(adc,AQADC)
lightSensor = LightSensor.LightSensor(adc,LightADC)
no2Sensor = MiCS2710.MiCS2710(adc,MiCSADC)

API_KEY = 'AaBeQoyPHcnC8rwEN2YJJbEKrJOSAKxBa0hEN08rblZUZz0g'
FEED = 85080

API_URL = '/v2/feeds/{feednum}.xml' .format(feednum=FEED)

# Continuously append data
while(True):
	dht.get_data()
	temp = dht.temp()
	humidity = dht.humidity()
	aq = airSensor.get_quality()
	lightlevels = lightSensor.get_light_level()
	bmptemp = bmp.readTemperature()
	pressure = bmp.readPressure()
	altitude = bmp.readAltitude()
	NO2 = no2Sensor.get_NO()

	if DEBUG:
		if temp!=False:
			#print "Temperature: %.1f C" % temp
			print "Humidity:    %.1f %%" % humidity
		else: print "Failed to read DHT22"
		print "Air Quality: %.2f AQ" % aq
		print "Light Level: %.2f Lux" % lightlevels
		print "Pressure:    %.1f Pa" % pressure
		print "Temp-2:      %.1f C" % bmptemp
		print "Altitude:    %.1f m" % altitude
		print "NO:          %.2f NO" % NO2

	aq = "%.2f" % aq
	lightlevels = "%.2f" % lightlevels

	if LOGGER:
		# Append the data in the spreadsheet, including a timestamp
		try:
			pac = eeml.Pachube(API_URL, API_KEY)
			if temp!=False:
				pac.update([eeml.Data(0, bmptemp, unit = eeml.Celsius())])    
				pac.update([eeml.Data(1, humidity, unit = eeml.RH())])
			pac.update([eeml.Data(2, aq)])
			pac.update([eeml.Data(3, lightlevels)])
			pac.update([eeml.Data(4, pressure)])
			pac.update([eeml.Data(6, NO2)])
			#pac.put()
			print "Uploaded data at " + str(datetime.datetime.now())
			GPIO.output(22, True)
		except:
			GPIO.output(21, True)
			print "Unable to upload data at " + str(datetime.datetime.now()) + ".  Check your connection?"
	for a in range(0,5):
		time.sleep(1)
		GPIO.output(22, False)
		GPIO.output(21, False)
		#dht.get_data() #constantly get data from DHT, but only save it if it validates.
