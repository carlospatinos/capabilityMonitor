import time
from tabulate import tabulate

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

class TimeoutProblem(RuntimeError):
	def __init__(self, arg):
		self.msg = arg
	def __str__(self):
		return self.msg

class ScenarioDefinition(object):
	def __init__(self, details, config):
		self.details = details
		self.config = config

	def __str__(self):
		return "Details: " + self.details + "\nConfig: " + self.config

	def getDetails(self):
		return self.details

	def getConfig(self):
		return self.config


class UseCaseResults(object):
	def __init__(self, useCaseName, sucessfullAssertions=0, failedAssertions=0, commands=dict()):
		self.useCaseName = useCaseName
		self.failedAssertions = failedAssertions
		self.sucessfullAssertions = sucessfullAssertions
		self.commands = commands

	def __str__(self):
		return "Name: " + self.useCaseName + bcolors.ENDC + bcolors.OKGREEN + "\tSucessfull Assertions: " + str(self.getSucessfuls()) + bcolors.WARNING + "\tFailed Assertions: " + str(self.getFailures()) + bcolors.ENDC + "\tTime Taken: " + str(self.getTimeTaken()) 
	def __repr__(self):
		return "Name: " + self.useCaseName + bcolors.ENDC + bcolors.OKGREEN + "\tSucessfull Assertions: " + str(self.getSucessfuls()) + bcolors.WARNING + "\tFailed Assertions: " + str(self.getFailures()) + bcolors.ENDC + "\tTime Taken: " + str(self.getTimeTaken()) 

	def getName(self):
		return self.useCaseName

	def getTotalAssertions(self):
		return self.failedAssertions + self.sucessfullAssertions

	def addCommandWithResponses(self, c, r):
		self.commands[c]=r

	def getCommands(self):
		return self.commands

	def startTimer(self):
		self.startTime = time.time()

	def endTimer(self):
		self.endTime = time.time()

	def getTimeTaken(self):
		return (self.endTime - self.startTime)

	def incrementFailures(self):
		self.failedAssertions+=1

	def getFailures(self):
		return self.failedAssertions

	def incrementSucessfuls(self):
		self.sucessfullAssertions+=1

	def getSucessfuls(self):
		return self.sucessfullAssertions

	def getFailuresAsStr(self):
		return bcolors.WARNING + str(self.failedAssertions) + bcolors.ENDC
	def getSucessesAsStr(self):
		return bcolors.OKGREEN + str(self.sucessfullAssertions) + bcolors.ENDC


class ScenarioExecutionResults(object):
	def __init__(self, executionTime, scenarioDetails, useCaseList, nodeName, vuser):
		self.executionTime = executionTime
		self.scenarioDetails = scenarioDetails
		self.useCaseList = useCaseList
		self.nodeName = nodeName
		self.vuser = vuser
		self.totalSucesses=0
		self.totalFailures=0

	def __str__(self):
		value = bcolors.BOLD + self.vuser + " executed scenario on node(s) " + self.getNodeName() + ". Start Time: " + self.executionTime + bcolors.ENDC + "\n\n" 
		#for uc in self.useCaseList:
		#	value = value + str(uc) + "\n"
		#scenatioExecutionResult=resultsFromExecution.get()
		resultsToPrint=[]
		for ucResults in self.useCaseList:
			resultsToPrint.append([ucResults.getName(), ucResults.getSucessesAsStr(), ucResults.getFailuresAsStr(), ucResults.getTimeTaken()])
			self.totalSucesses+=ucResults.getSucessfuls()
			self.totalFailures+=ucResults.getFailures()
		
		value = value + tabulate(resultsToPrint, headers=['UseCase Name', bcolors.OKGREEN + 'Sucessfull Assertions' + bcolors.ENDC, bcolors.WARNING + 'Failed Assertions' + bcolors.ENDC, 'Time Taken'], tablefmt="grid")
		return value

	def getExecutionTime(self):
		return self.executionTime

	def getUseCaseList(self):
		return self.useCaseList

	def getNodeName(self):
		return self.nodeName

class CommandLineParser(object):
	#
	#	Layout:
	#		resultListFromSplit[0] = command to execute
	cliCommandPosition=0
	expectedValuePosition=1

	def __init__(self, command, expressionWithCommand, delimiter):
		self.expressionWithCommand = expressionWithCommand
		self.command = command
		self.delimiter = delimiter
		self.resultListFromSplit = []
		self.removeExpressionAndParse()

	def removeExpressionAndParse(self):
		self.resultListFromSplit = self.command.replace(self.expressionWithCommand, "").split(self.delimiter)

	def getResultListFromSpit(self):
		return self.resultListFromSplit

	def getCliCommandToExecute(self):
		return self.resultListFromSplit[self.cliCommandPosition]

	def getExpectedValue(self):
		return self.resultListFromSplit[self.expectedValuePosition]

	def getResultListFromSpitAtPosition(self, position):
		return self.resultListFromSplit[position]

	def isCliCommand(self):
		if self.resultListFromSplit[self.cliCommandPosition].startswith("cmedit"):
			return True
		else: 
			return False;