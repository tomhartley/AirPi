import MCP3008

class LightSensor:
	adc = None
	adcPin = 0
	
	def __init__(self, adc, adcNumber):
		self.adc = adc
		self.adcPin = adcNumber
	
	def get_light_level(self):
		result = self.adc.readADC(self.adcPin) + 1
		vout = float(result)/1023 * 3.3
		rs = ((3.3 - vout) / vout) * 5.6
		return rs
