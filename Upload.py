#!/usr/bin/python

from time import sleep
import datetime
import eeml
import subprocess, os, sys
import RPi.GPIO as GPIO
from interfaces.DHT22 import DHT22
from interfaces.BMP085 import BMP085
from interfaces.MCP3008 import MCP3008, AQSensor, LightSensor
from interfaces.PiPlate import Adafruit_CharLCDPlate

lcd = Adafruit_CharLCDPlate.Adafruit_CharLCDPlate()
lcd.clear()
lcd.backlight(lcd.ON)
lcd.message("     AirPi\n by Alyssa & Tom")
sleep(2)
lcd.clear()
lcd.message("Air Quality and \nWeather Station")
os.chdir(os.path.dirname(sys.argv[0]))

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
NO2ADC = 2
COADC = 3
UVADC = 4

dht = DHT22.DHT22(DHTPin)
bmp = BMP085.BMP085(bus=bus)
adc = MCP3008.MCP3008(SPIMOSI,SPIMISO,SPICLK,SPICS)
airSensor = AQSensor.AQSensor(adc,AQADC,22000)
lightSensor = LightSensor.LightSensor(adc,LightADC)
uvSensor = LightSensor.LightSensor(adc,UVADC)
no2Sensor = AQSensor.AQSensor(adc,NO2ADC,90000,10000)
coSensor = AQSensor.AQSensor(adc,COADC,190000,100000)


API_KEY = 'AaBeQoyPHcnC8rwEN2YJJbEKrJOSAKxBa0hEN08rblZUZz0g'
FEED = 85080

API_URL = '/v2/feeds/{feednum}.xml' .format(feednum=FEED)
failCount = 0
currentDisplay = 0
# Continuously append data
while(True):
	dht.get_data()
	temp = dht.temp()
	humidity = dht.humidity()
	aq = airSensor.get_quality()
	lightlevels = lightSensor.get_light_level()
	uvlevels = uvSensor.get_uv_level()
	bmptemp = bmp.readTemperature()
	pressure = bmp.readPressure()
	altitude = bmp.readAltitude()
	NO2 = no2Sensor.get_NO2()
	CO = coSensor.get_CO()
	NO2res = no2Sensor.get_quality()
	COres = coSensor.get_quality()
	if DEBUG:
		if temp!=False:
			print "Temp-DHT:    %.1f C" % temp
			print "Humidity:    %.1f %%" % humidity
		else: print "Failed to read DHT22"
		print "Air Quality: %.2f Ohms" % aq
		print "Light Level: %.2f Lux" % lightlevels
		print "UV Level:    %.2f UVI" % uvlevels
		print "Pressure:    %.1f Pa" % pressure
		print "Temp-BMP:    %.1f C" % bmptemp
		print "Altitude:    %.1f m" % altitude
		print "NO2:         %.3f ppm" % NO2
		print "CO:          %.3f ppm" % CO
		print "NO2 ohms:    %.1f Ohms" % NO2res
                print "CO ohms:     %.1f Ohms" % COres
	aqfor = "%.1f" % aq
	COfor = "%.3f" % CO
	NO2for = "%.3f" % NO2
	NO2resfor = str(int(NO2res))
	COresfor = str(int(COres))
	lightlevelsfor = "%.2f" % lightlevels
	uvlevelsfor = "%.2f" % uvlevels

	if LOGGER:
		#Attempt to submit the data to cosm
		try:
			pac = eeml.Pachube(API_URL, API_KEY)
			pac.update([eeml.Data(0, bmptemp)])
			if temp!=False:
				pac.update([eeml.Data(1, humidity)])
			pac.update([eeml.Data(2, aqfor)])
			pac.update([eeml.Data(3, lightlevelsfor)])
			pac.update([eeml.Data(4, pressure)])
			pac.update([eeml.Data(5, COfor)])
			pac.update([eeml.Data(6, NO2for)])
			pac.update([eeml.Data(7, COresfor)])
			pac.update([eeml.Data(8, NO2resfor)])
			pac.update([eeml.Data(9, uvlevelsfor)])
			pac.put()
			print "Uploaded data at " + str(datetime.datetime.now())
			GPIO.output(22, True)
			lcd.backlight(lcd.GREEN)
			failCount = 0
		except:
			GPIO.output(21, True)
			lcd.backlight(lcd.ON)
			print "Unable to upload data at " + str(datetime.datetime.now()) + ".  Check your connection?"
			failCount+=1
			if failCount>23:
				subprocess.call(["sudo", "/etc/init.d/networking", "restart"])
				failCount=0
	lcd.clear()
	if (currentDisplay == 0):
		lcd.message("Temp: %.1fC\nHumidity: %.1f%%" % (bmptemp,humidity))
	elif (currentDisplay == 1):
		lcd.message("Pres: %.2f hPa\nSmoke: %.2f"%(pressure/100.0,aq/1000))
	elif (currentDisplay == 2):
		lcd.message("UV: %.2f UVI\nLight: %.2f lx"%(uvlevels,lightlevels))
	else:
		lcd.message("NO2: %.2f ppm\nCO: %.2f ppm"%(NO2,CO)) 
	#lcd.message("Temp: %.1fC"%bmptemp)
	sleep(1.5)
	GPIO.output(22, False)
	GPIO.output(21, False)
	currentDisplay+=1
	if currentDisplay == 4:
		currentDisplay = 0
	#for a in range(0,5):
	#	time.sleep(0.2)
	#	GPIO.output(22, False)
	#	GPIO.output(21, False)
	#	#dht.get_data() #constantly get data from DHT, but only save it if it validates.
