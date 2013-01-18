import MCP3008

class MiCS2710:
	adc = None
	adcPin = 2
	
	def __init__(self, adc, adcNumber):
		self.adc = adc
		self.adcPin = adcNumber
	
	def get_NO(self):
		result = self.adc.readADC(self.adcPin) + 1
		vout = float(result)/1023 * 3.3
		rs = ((5.0 - vout) / vout)
		return rs
