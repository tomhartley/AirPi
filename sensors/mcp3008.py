#!/usr/bin/python

import RPi.GPIO as GPIO
import sensor

class MCP3008(sensor.Sensor):
	requiredData = []
	optionalData = ["mosiPin","misoPin","csPin","clkPin"]
	sharedClass = None
	def __init__(self, data):
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		self.SPIMOSI = 23
		self.SPIMISO = 24
		self.SPICLK = 18
		self.SPICS = 25
		if "mosiPin" in data:
			self.SPIMOSI = data["mosiPin"]
		if "misoPin" in data:
			self.SPIMISO = data["misoPin"]
		if "clkPin" in data:
			self.SPICLK = data["clkPin"]
		if "csPin" in data:
			self.SPICS = data["csPin"] 
		GPIO.setup(self.SPIMOSI, GPIO.OUT)
		GPIO.setup(self.SPIMISO, GPIO.IN)
		GPIO.setup(self.SPICLK, GPIO.OUT)
		GPIO.setup(self.SPICS, GPIO.OUT)
		if MCP3008.sharedClass == None:
			MCP3008.sharedClass = self

	#read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
	def readADC(self,adcnum):
		if ((adcnum > 7) or (adcnum < 0)):
			return -1
		GPIO.output(self.SPICS, True)

		GPIO.output(self.SPICLK, False)  # start clock low
		GPIO.output(self.SPICS, False)     # bring CS low

		commandout = adcnum
		commandout |= 0x18  # start bit + single-ended bit
		commandout <<= 3    # we only need to send 5 bits here
		for i in range(5):
			if (commandout & 0x80):
				GPIO.output(self.SPIMOSI, True)
			else:
	   			GPIO.output(self.SPIMOSI, False)
	                commandout <<= 1
	                GPIO.output(self.SPICLK, True)
	                GPIO.output(self.SPICLK, False)

		adcout = 0
		# read in one empty bit, one null bit and 10 ADC bits
		for i in range(11):
			GPIO.output(self.SPICLK, True)
			GPIO.output(self.SPICLK, False)
			adcout <<= 1
			if (GPIO.input(self.SPIMISO)):
				adcout |= 0x1

		GPIO.output(self.SPICS, True)
		return adcout
	
	def getVal(self):
		return None #not that kind of plugin, this is to be used by other plugins
