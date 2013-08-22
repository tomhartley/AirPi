import output

class Print(output.Output):
	requiredData = []
	optionalData = []
	def __init__(self,data):
		pass
	def uploadData(self,dataPoints):
		for i in dataPoints:
			print i["name"] + ": " + str(i["value"]) + " " + i["unit"]
