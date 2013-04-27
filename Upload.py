#!/usr/bin/python

from time import sleep
from sys import exit
import ConfigParser
import os.path
import datetime
import eeml
import eeml.datastream
import subprocess, os, sys
import RPi.GPIO as GPIO
from interfaces.DHT22 import DHT22
from interfaces.BMP085 import BMP085
from interfaces.MCP3008 import MCP3008, MCP3208, AQSensor, LightSensor
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
	# Load the config file if it exists
        if not os.path.isfile('AirPi.cfg'):
		print "Unable to access config file : AirPi.cfg"
                exit(1)
	config = ConfigParser.ConfigParser()
        print config.read('AirPi.cfg')
        

	WDOGON = config.getboolean("AirPi", "Watchdog")
	if WDOGON:
		sleep(1)
		wdog = os.open('/dev/watchdog',os.O_RDWR)
	try:
		# Get basic options from config file
		bus = config.getint("AirPi", "I2CBus")
		LCDENABLED = config.getboolean("AirPi", "LCD")
		DEBUG = config.getboolean("AirPi", "Debug")
		LOGGER = config.getboolean("Cosm", "Enabled")
		FREQUENCY = config.getint("AirPi", "Frequency")
		NETRESTART = config.getboolean("AirPi", "NetRestart")
		NETRETRIES = config.getint("AirPi", "NetRetries")

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
	
		
		if not DEBUG:
	                GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(22,GPIO.OUT)
		GPIO.setup(21,GPIO.OUT)

                # Get the ADC details from the config			
		SPIMOSI = config.getint("ADC", "MOSI")
		SPIMISO = config.getint("ADC", "MISO")
		SPICLK = config.getint("ADC", "CLK")
		SPICS = config.getint("ADC", "CS")
                adc = config.get("ADC", "ADC").lower()
                if adc == 'mcp3008':
			adc = MCP3008.MCP3008(SPIMOSI,SPIMISO,SPICLK,SPICS)
                elif adc == 'mcp3208':
			adc = MCP3208.MCP3208(SPIMOSI,SPIMISO,SPICLK,SPICS)
                else:
			print "You must specify a valid ADC in AirPi.cfg"
			exit(1)

		# Get the DHT22 details from the config	
		DHTEn = config.getboolean("DHT22", "Enabled")
                if DHTEn:
			DHTPin = config.getint("DHT22", "DHTPin")
			dht = DHT22.DHT22(DHTPin)
                
		# Get the BMP085 details from the config
		BMPEn = config.getboolean("BMP085", "Enabled")
		if BMPEn: 
			bmp = BMP085.BMP085(bus=bus)
			BMPMSLP = config.getboolean("BMP085", "MSLP")
                        BMPALT = config.getint("BMP085", "Altitude")

		# Get the UVI-01 details from the config
		UVIEn = config.getboolean("UVI-01", "Enabled")
		if UVIEn:
			UVADC = config.getint("UVI-01", "ADCPin")
			uvSensor = LightSensor.LightSensor(adc,UVADC)

		# Get the LDR details from the config
		LDREn = config.getboolean("LDR", "Enabled")
		if LDREn:
			LightADC = config.getint("LDR", "ADCPin")
			lightSensor = LightSensor.LightSensor(adc,LightADC)

		# Get the TGS2600 details from the config
		TGSEn = config.getboolean("TGS2600", "Enabled")
		if TGSEn:
			AQADC = config.getint("TGS2600", "ADCPin")
			pullup = config.getint("TGS2600", "PullUp")
			airSensor = AQSensor.AQSensor(adc,AQADC,pullup)

		# Get the MICS-2710 details from the config
                NO2En = config.getboolean("MICS-2710", "Enabled")
		if NO2En:
			NO2ADC = config.getint("MICS-2710", "ADCPin")
			pullup = config.getint("MICS-2710", "PullUp")
			resist = config.getint("MICS-2710", "Resistance")
			no2Sensor = AQSensor.AQSensor(adc,NO2ADC,resist,pullup)

		# Get the MICS-5525 details from the config
		COEn = config.getboolean("MICS-5525", "Enabled")
		if COEn:
			COADC = config.getint("MICS-5525", "ADCPin")
			pullup = config.getint("MICS-5525", "PullUp")
			resist = config.getint("MICS-5525", "Resistance")
			coSensor = AQSensor.AQSensor(adc,COADC,resist,pullup)
		
		if LOGGER:
			API_KEY = config.get("Cosm", "APIKEY", 1)
			FEED = config.getint("Cosm", "FEEDID")
			API_URL = '/v2/feeds/{feednum}.xml' .format(feednum=FEED)
		failCount = 0
		currentDisplay = 0
		
		# Continuously append data
		while(True):
			if WDOGON:
				os.write(wdog,"0")
			datas = []
			if DHTEn:
				dht.get_data()
				d = DataPoint(dht.temp(),"Temp-DHT","C",1,-1)
				if d.value != False:
					datas.append(d)
					datas.append(DataPoint(dht.humidity(),"Humidity","%",1,1,"Humidity"))
			if TGSEn:
				datas.append(DataPoint(airSensor.get_quality(),"Air Quality"," ",2,2,"AQ"))
			if LDREn:
				datas.append(DataPoint(lightSensor.get_light_level(),"Light Level","Lux",2,3,"Light"))
			if UVIEn:
				datas.append(DataPoint(uvSensor.get_uv_level(),"UV Level","UVI",2,9,"UV"))
			if BMPEn:
				datas.append(DataPoint(bmp.readTemperature(),"Temp-BMP","C",1,0,"Temp"))
				if BMPMSLP:
					datas.append(DataPoint(bmp.readMSLPressure(BMPALT),"Pressure","Pa",1,4,"Pres"))
                        	else:
					datas.append(DataPoint(bmp.readPressure(),"Pressure","Pa",1,4,"Pres"))
					datas.append(DataPoint(bmp.readAltitude(),"Altitude","m",1,-1))
			if NO2En:
				datas.append(DataPoint(no2Sensor.get_NO2(),"NO2","ppm",3,6,"NO2"))
				datas.append(DataPoint(no2Sensor.get_quality(),"NO2 ohms","ohms",1,8))
			if COEn:
				datas.append(DataPoint(coSensor.get_CO(),"CO","ppm",3,5,"CO"))
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
					if NETRESTART:
						failCount+=1
						if failCount>NETRETRIES:
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
			sleep(FREQUENCY-1)
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
