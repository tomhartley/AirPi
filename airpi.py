#This file takes in inputs from a variety of sensor files, and outputs information to a variety of services

import ConfigParser
import time
import inspect
import os
from sys import exit
from sensors import sensor

def get_subclasses(mod,cls):
	for name, obj in inspect.getmembers(mod):
		if hasattr(obj, "__bases__") and cls in obj.__bases__:
			return obj


if not os.path.isfile('sensors.cfg'):
	print "Unable to access config file: sensors.cfg"
	exit(1)

sensorConfig = ConfigParser.SafeConfigParser()
sensorConfig.read('sensors.cfg')

sensorNames = sensorConfig.sections()


sensorPlugins = []
for i in sensorNames:
	try:	
		try:
			filename = sensorConfig.get(i,"filename")
		except:
			print("Error: no filename config option found for " + i)
			raise
		try:
			enabled = sensorConfig.getboolean(i,"enabled")
		except:
			enabled = True

		#if enabled, load the plugin
		if enabled:
			try:
				mod = __import__('sensors.'+filename,fromlist=['a']) #Why does this work?
			except:
				print("Error: could not import module " + filename)
				raise

			try:	
				sensorClass = get_subclasses(mod,sensor.Sensor)
				if sensorClass == None:
					raise AttributeError
			except:
				print("Error: could not find a subclass of sensor.Sensor in module " + filename)
				raise

			try:	
				reqd = sensorClass.requiredData
			except:
				reqd =  []
			try:
				opt = sensorClass.optionalData
			except:
				opt = []

			pluginData = {}

			class MissingField(Exception): pass
						
			for requiredField in reqd:
				if sensorConfig.has_option(i,requiredField):
					pluginData[requiredField]=sensorConfig.get(i,requiredField)
				else:
					print "Error: Missing required field '" + requiredField + "' for sensor plugin " + i
					raise MissingField
			for optionalField in opt:
				if sensorConfig.has_option(i,optionalField):
					pluginData[optionalField]=sensorConfig.get(i,optionalField)
			instClass = sensorClass(pluginData)
			sensorPlugins.append(instClass)
			print ("Success: Loaded sensor plugin " + i)
	except Exception as e: #add specific exception for missing module
		print("Error: Did not import sensor plugin " + i )
		raise e


if not os.path.isfile("outputs.cfg"):
	print "Unable to access config file: outputs.cfg"

outputConfig = ConfigParser.SafeConfigParser()
outputConfig.read("outputs.cfg")
