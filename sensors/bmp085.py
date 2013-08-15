import sensor

class Bmp085(sensor.Sensor):
	requiredData = ["measurement","i2cport"]
	optionalData = ["altitude","mslp","unit"]
	def __init__(self,data):
		print data
		if "temp" in data["measurement"].lower():
			self.valName = "Temperature"
			self.valUnit = "C"
			if "unit" in data:
				if data["unit"]=="F":
					self.valUnit = "F"
			self.sigfigs = 3
		elif "pres" in data["measurement"].lower():
			self.valName = "Pressure"
			self.valUnit = "hPa"
			self.sigfigs = 3
			self._altitude = 0
			if "mslp" in data:
				if data["mslp"].lower in ["on","true","1","yes"]:
					if "altitude" in data:
						self.altitude=data["altitude"]
		
		return

	def getVal(self):
		return 0
