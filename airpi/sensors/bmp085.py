import sensor
import bmpBackend

class Bmp085(sensor.Sensor):
	bmpClass = None
	requiredData = ["measurement","i2cbus"]
	optionalData = ["altitude","mslp","unit"]
	def __init__(self,data):
		self.sensorName = "BMP085"
		if "temp" in data["measurement"].lower():
			self.valName = "Temperature"
			self.valUnit = "Celsius"
			self.valSymbol = "C"
			self.mslp = False
			if "mslp" in data:
				self.mslp = data["mslp"]
				if self.mslp:
					if "altitude" in data:
						self.altitude = data["altitude"]
					else:
						print "To calculate MSLP, please provide an 'altitude' config setting for the BMP085 (in m)"
						self.mslp = False
			if "unit" in data:
				if data["unit"]=="F":
					self.valUnit = "Farenheight"
					self.valSymbol = "F"
		elif "pres" in data["measurement"].lower():
			self.valName = "Pressure"
			self.valSymbol = "hPa"
			self.valUnit = "Hectopascal"
			self._altitude = 0
			if "mslp" in data:
				if data["mslp"].lower in ["on","true","1","yes"]:
					if "altitude" in data:
						self.altitude=data["altitude"]
		if (!bmpClass):
			bmpClass = bmpBackend.BMP085(bus=bus)
		return

	def getVal(self):
		if self.valName = "Temperature":
			temp = bmpClass.readTemperature()
			if self.valUnit = "Fahrenheit":
				temp = temp * 1.8 + 32
			return temp
		elif self.valName = "Pressure":
			if self.mslp:
				return self.bmpClass.readMSLPressure(self.altitude) * 0.01 #to convert to Hectopascals
			else:
				return self.bmpClass.readPressure() * 0.01 #to convert to Hectopascals