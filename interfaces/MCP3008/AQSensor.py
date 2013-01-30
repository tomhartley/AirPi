import MCP3008

class AQSensor:
	adc = None
	adcPin = 0
	
	def __init__(self, adc, adcNumber, pullup = 10000):
		self.adc = adc
		self.adcPin = adcNumber
		self.pullup = pullup
	
	def get_quality(self):
		result = float(self.adc.readADC(self.adcPin))
		resistance = (1550/result - 1)*self.pullup
		return resistance
