#!/usr/bin/python

from time import sleep
import datetime
import eeml
import eeml.datastream
import subprocess, os, sys
import RPi.GPIO as GPIO
from interfaces.DHT22 import DHT22
from interfaces.BMP085 import BMP085
from interfaces.MCP3008 import MCP3008, AQSensor, LightSensor
from interfaces.PiPlate import Adafruit_CharLCDPlate
import curses

class DataPoint():
	def __init__(self,value,name,unit,decimalplaces,uploadID,shortName=None):
		self.value = value
		self.name = name
		self.unit = unit
		self.decimals = decimalplaces
		self.uploadID = uploadID
		self.sName = shortName
	def roundedValue(self):
		formatString = '{0:.' + str(self.decimals) + 'f}'
		return formatString.format(self.value)

def mainUpload(stdscr):
	WDOGON = 0
	if WDOGON:
		sleep(1)
		wdog = os.open('/dev/watchdog',os.O_RDWR)
	try:
		bus = 0
		
		LCDENABLED = 1
		DEBUG = 1
		LOGGER = 1
		
		if LCDENABLED:
			lcd = Adafruit_CharLCDPlate.Adafruit_CharLCDPlate(busnum=bus)
			lcd.clear()
			lcd.backlight(lcd.ON)
			lcd.message("     AirPi\n by Alyssa & Tom")
			sleep(2)
			lcd.clear()
			lcd.message("Air Quality and \nWeather Station")
	
		try:
			os.chdir(os.path.dirname(sys.argv[0]))
		except:
			pass
	
		DHTPin = 4
		
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(22,GPIO.OUT)
		GPIO.setup(21,GPIO.OUT)
			
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
		airSensor = AQSensor.AQSensor(adc,AQADC,pullup=22000)
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
			if WDOGON:
				os.write(wdog,"0")
			datas = []
			dht.get_data()
			d = DataPoint(dht.temp(),"Temp-DHT","C",1,-1)
			if d.value != False:
				datas.append(d)
				datas.append(DataPoint(dht.humidity(),"Humidity","%",1,1,"Humidity"))
			datas.append(DataPoint(airSensor.get_quality(),"Air Quality"," ",2,2,"AQ"))
			datas.append(DataPoint(lightSensor.get_light_level(),"Light Level","Lux",2,3,"Light"))
			datas.append(DataPoint(uvSensor.get_uv_level(),"UV Level","UVI",2,9,"UV"))
			datas.append(DataPoint(bmp.readTemperature(),"Temp-BMP","C",1,0,"Temp"))
			datas.append(DataPoint(bmp.readPressure(),"Pressure","Pa",1,4,"Pres"))
			datas.append(DataPoint(bmp.readAltitude(),"Altitude","m",1,-1))
			datas.append(DataPoint(no2Sensor.get_NO2(),"NO2","ppm",3,6,"NO2"))
			datas.append(DataPoint(coSensor.get_CO(),"CO","ppm",3,5,"CO"))
			datas.append(DataPoint(no2Sensor.get_quality(),"NO2 ohms","ohms",1,8))
			datas.append(DataPoint(coSensor.get_quality(),"CO ohms","ohms",1,7))
			if DEBUG and (stdscr == None):
				for dp in datas:
					print dp.name + ":\t" + dp.roundedValue() + " " + dp.unit
			if stdscr != None:
				a = 0
				for dp in datas:
					if dp.uploadID != -1:
						a+=1
						stdscr.addstr(5 + (a * 2), 3, dp.name + ":\t" + dp.roundedValue() + " " + dp.unit)
						stdscr.clrtoeol()
				stdscr.refresh() 
			if LOGGER:
				#Attempt to submit the data to cosm
				try:
					pac = eeml.datastream.Cosm(API_URL, API_KEY)
					for dp in datas:
						if dp.uploadID!=-1:
							pac.update([eeml.Data(dp.uploadID, dp.roundedValue())])
					pac.put()
					if stdscr == None:
						print "Uploaded data at " + str(datetime.datetime.now())
					GPIO.output(22, True)
					if LCDENABLED:		
						lcd.backlight(lcd.GREEN)
					failCount = 0
				except KeyboardInterrupt:
					raise
				except:
					GPIO.output(21, True)
					if LCDENABLED:
						lcd.backlight(lcd.ON)
					print "Unable to upload data at " + str(datetime.datetime.now()) + ".  Check your connection?"
					failCount+=1
					if failCount>15:
						subprocess.Popen(["sudo", "/etc/init.d/networking", "restart"])
						failCount=0
	
			if LCDENABLED:
				usedValues = []
				for a in datas:
					if a.sName!=None:
						usedValues.append(a)
				data1 = usedValues[currentDisplay*2]
				data2 = usedValues[currentDisplay*2 + 1]
				lcd.clear()
				lcd.message(data1.sName + ": " + data1.roundedValue() + " " + data1.unit + "\n" + data2.sName + ": " + data2.roundedValue() + " " + data2.unit)
			sleep(1.5)
			GPIO.output(22, False)
			GPIO.output(21, False)
			currentDisplay+=1
			if currentDisplay == 4:
				currentDisplay = 0
	except KeyboardInterrupt:
		if WDOGON:
			os.write(wdog,"V")
			os.close(wdog)
		raise	

cursesEnabled = 0
if cursesEnabled:
	curses.wrapper(mainUpload)
else:
	mainUpload(None)
