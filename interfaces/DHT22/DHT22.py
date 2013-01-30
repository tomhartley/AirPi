#!/usr/bin/python

import subprocess, os
import re

class DHT22:
	DHTPin = 0
	output = ""
	def __init__(self, pin):
		self.DHTPin = pin
		try:
			os.chdir('interfaces/DHT22')
		except:
			print "os.chdir failed"
	
	def get_data(self):
		oldOutput = self.output
		try:
			self.output = subprocess.check_output(["timeout", "3","./Adafruit_DHT", "22", str(self.DHTPin)]);
		except:
			print "Operation timed out"
		if self.temp()==False:
			self.output = oldOutput

	def temp(self):
		#print output
		matches = re.search("Temp =\s+([0-9.]+)", self.output)
		if (not matches):
			return False
		return float(matches.group(1))

	def humidity(self):
		# search for humidity printout
		matches = re.search("Hum =\s+([0-9.]+)", self.output)
		if (not matches):
			return False
		return float(matches.group(1))
