#This file takes in inputs from a variety of sensor files, and outputs information to a variety of services

import ConfigParser
import time
import importlib
import inspect
from sys import exit

def get_subclasses(mod,cls):
	for name, obj in inspect.getmembers(mod):
		if hasattr(obj, "__bases__" and cls in obj.__bases__:
			return obj

sensorPlugins = []

if not os.path.isfile('sensors.cfg'):
	print "Unable to access config file: sensors.cfg"
	exit(1)


sensorConfig = ConfigParser.SafeConfigParser()
sensorConfig.read('sensors.cfg')

sensorNames = sensorConfig.sections()
for i in sensorNames:
	filename = sensorConfig.get(i,"filename")
	enabled = sensorConfig.getboolean(i,"enabled")
	#if enabled, load the plugin
	try:
		mod = importlib.import_module(filename,"sensors")
	except: #add specific exception for missing module
		print("Could not import module " + filename")
	
