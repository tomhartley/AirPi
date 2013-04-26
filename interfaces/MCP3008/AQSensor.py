import MCP3008

class AQSensor:
	adc = None
	adcPin = 0
	
	def __init__(self, adc, adcNumber, r0=10000, pullup = 10000):
		self.adc = adc
		self.adcPin = adcNumber
		self.pullup = pullup
		self.r0 = r0
	
	def get_quality(self):
		result = float(self.adc.readADC(self.adcPin))
		if result == 0:
			resistance = 0
		else:
			vin = ((2**self.adc.ADCBITS) / 3.3) * 5
			resistance = (vin/result - 1)*self.pullup
		return resistance
	
	def get_NO2(self):
		conversions = [((0,100),(0,0.25)),((100,133),(0.25,0.325)),((133,167),(0.325,0.475)),((167,200),(0.475,0.575)),((200,233),(0.575,0.665)),((233,267),(0.666,0.75))]
		rs = self.get_quality()
		rsper = 100*(float(rs)/self.r0)
		for a in conversions:
			if a[0][0]<=rsper<a[0][1]:
				mid,hi = rsper-a[0][0],a[0][1]-a[0][0]
				sf = float(mid)/hi
				ppm = sf * (a[1][1]-a[1][0]) + a[1][0]
				return ppm
		return rsper * 0.002808988764

	def get_CO(self):
		conversions = [((110,90),(0,1.5)),((90,85),(1.5,5)),((85,80),(5,6)),((80,75),(6,7)),((75,70),(7,8)),((70,65),(8,12)),((65,60),(12,14)),((60,55),(14,18)),((55,50),(18,22))]
		rs = self.get_quality()
                rsper = 100*(float(rs)/self.r0)
                for a in conversions:
                        if a[0][0]>=rsper>a[0][1]:
                                mid,hi = rsper-a[0][0],a[0][1]-a[0][0]
                                sf = float(mid)/hi
                                ppm = sf * (a[1][1]-a[1][0]) + a[1][0]
                                return ppm
                if rsper>110:
			return 0
		else:
			return (1/float(rsper))*1100

