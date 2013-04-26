#!/usr/bin/python

import RPi.GPIO as GPIO

class MCP3008:
	SPIMOSI = 0
	SPIMISO = 0
	SPICLK = 0
	SPICS = 0
        ADCBITS=10

	def __init__(self, mosipin, misopin, clkpin, cspin):
		GPIO.setmode(GPIO.BCM)
		self.SPIMOSI = mosipin
		self.SPIMISO = misopin
		self.SPICLK = clkpin
		self.SPICS = cspin
		GPIO.setup(self.SPIMOSI, GPIO.OUT)
		GPIO.setup(self.SPIMISO, GPIO.IN)
		GPIO.setup(self.SPICLK, GPIO.OUT)
		GPIO.setup(self.SPICS, GPIO.OUT)

	# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
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
		for i in range(self.ADCBITS+1):
			GPIO.output(self.SPICLK, True)
			GPIO.output(self.SPICLK, False)
			adcout <<= 1
			if (GPIO.input(self.SPIMISO)):
				adcout |= 0x1

		GPIO.output(self.SPICS, True)
		return adcout
