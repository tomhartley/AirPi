import sensor
import bmpBackend

class BMP085(sensor.Sensor):
	bmpClass = None
	requiredData = ["measurement","i2cbus"]
	optionalData = ["altitude","mslp","unit"]
	def __init__(self,data):
		self.sensorName = "BMP085"
		if "temp" in data["measurement"].lower():
			self.valName = "Temperature"
			self.valUnit = "Celsius"
			self.valSymbol = "C"
			if "unit" in data:
				if data["unit"]=="F":
					self.valUnit = "Fahrenheit"
					self.valSymbol = "F"
		elif "pres" in data["measurement"].lower():
			self.valName = "Pressure"
			self.valSymbol = "hPa"
			self.valUnit = "Hectopascal"
			self.altitude = 0
			self.mslp = False
			if "mslp" in data:
				if data["mslp"].lower in ["on","true","1","yes"]:
					self.mslp = True
					if "altitude" in data:
						self.altitude=data["altitude"]
					else:
						print "To calculate MSLP, please provide an 'altitude' config setting (in m) for the BMP085 pressure module"
						self.mslp = False
		if (BMP085.bmpClass==None):
			BMP085.bmpClass = bmpBackend.BMP085(bus=int(data["i2cbus"]))
		return

	def getVal(self):
		if self.valName == "Temperature":
			temp = BMP085.bmpClass.readTemperature()
			if self.valUnit == "Fahrenheit":
				temp = temp * 1.8 + 32
			return temp
		elif self.valName == "Pressure":
			if self.mslp:
				return BMP085.bmpClass.readMSLPressure(self.altitude) * 0.01 #to convert to Hectopascals
			else:
				return BMP085.bmpClass.readPressure() * 0.01 #to convert to Hectopascals
