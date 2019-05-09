#!/usr/bin/env python
import enmscripting
import logging
import time
import Queue
import threading
import json
import glob
import sys
import argparse
import os.path

import urllib2
import requests
import httplib

from threading import Thread, current_thread

import support

#Default values if not provided by command line
enmUrl = "" #vapp
enmPass = ""
enmUser = ""

executionPlan=""
restService="http://localhost:8081/dataForGraphics/haDataReal"

#AVAILABLE COMMANDS IN CFG
WAIT_CONSTANT="WAIT_FOR:"
VALIDATE_CONST_VAL_IN_RESP="VALIDATE_RESPONSE_HAS_CONST_FOR:"
VALIDATE_CONST_VAL_NOT_IN_RESP="VALIDATE_RESPONSE_DONT_CONTAINS_EXP_VAL_FOR:"
VALIDATE_VARIABLE_VAL_IN_RESP="VALIDATE_RESPONSE_HAS_VARIABLE_FOR:"
STORE_LAST_LINE_FOR="STORE_LAST_LINE_FOR:"
REPLACE_IN_STORED_VARIABLE="REPLACE_IN_STORED_VARIABLE:"
INCREMENT_STORED_VARIABLE="INCREMENT_STORED_VARIABLE:"
DECREMENT_STORED_VARIABLE="DECREMENT_STORED_VARIABLE:"
APPEND_TO_STORED_VARIABLE="APPEND_TO_STORED_VARIABLE:"
VALIDATE_FIRST_LESSTHAN_SECOND_VAR="VALIDATE_FIRST_LESSTHAN_SECOND_VAR:"
SINGLE_FOR="SINGLE_FOR:"
BATCH_FOR="BATCH_FOR:"
#RANDOM_STR_VALUE_PER_DAY="$RANDOM_STR_VALUE_PER_DAY$"

#Constant values
LOG_FILE_NAME='ha-validation-tool.log'
CLI_LOG_FILE="cli-script-tool.log"
DELIMITER="|"
COMMENTED_LINE="#"
COMMAND_TIME_OUT=120 # seconds

session=0
logger=0
scenariosConfiguration=0
iterationNumber=0
sleepTime=5
globalDictionaryForStoredValues=dict()

def configLoggin():
	global logger
	logging.basicConfig(filename=CLI_LOG_FILE, level=logging.INFO)
	logger = logging.getLogger('haValidationTool')
	logger.setLevel(logging.DEBUG)
	# create file handler which logs even debug messages
	fh = logging.FileHandler(LOG_FILE_NAME)
	# create formatter and add it to the handlers
	formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')
	fh.setFormatter(formatter)
	logger.addHandler(fh)

def setUpScript():
	global executionPlan, virtualUsers,enmUrl,iterationNumber,sleepTime
	parser = argparse.ArgumentParser(description='Running HA Scenarios against enm iso.')
	parser.add_argument('-p', action="store", dest="execution_plan", help='Execution plan to be run. i.e. enm_cleanup_plan.cfg', required=True)
	parser.add_argument('-v', action="store", dest="virtual_users", type=int,help='Number of virtual users.', default=5)
	parser.add_argument('-u', action="store", dest="cli_url", help='URL for cli. Gateway should be up and running in case of vapp', default="")
	parser.add_argument('-l', action="store", dest="log_level", help='Level of logging', default="INFO")
	parser.add_argument('-i', action="store", dest="iterations", type=int, help='Number of iterations', default=1)
	parser.add_argument('-s', action="store", dest="sleepTime", type=int, help='Sleep time between iteration', default=5)
	parser.add_argument('-r', action="store", dest="restService", help='Rest Service Endpoint to save results.', default="http://localhost:3000/dataForGraphics/haDataReal")
	nameSpace=parser.parse_args()

	executionPlan=nameSpace.execution_plan
	virtualUsers=nameSpace.virtual_users
	enmUrl=nameSpace.cli_url
	iterationNumber=nameSpace.iterations
	sleepTime=nameSpace.sleepTime
	#print "Parsed parameters from command line are: executionPlan [",executionPlan,"], virtualUsers [",virtualUsers,"], enmUrl[",enmUrl,"]"
	configLoggin()

	printExecutionConfiguration()

def main():
	scenariosConfiguration = loadAllCfgScenariosIntoDictionary()
	scenarioToExecute = Queue.Queue()
	resultsFromExecution = Queue.Queue()

	vUserId=1
	for i in xrange(virtualUsers): #number of consumers
		t = threading.Thread(target=processEventFromQueueToExecuteScenario, args = (scenarioToExecute, resultsFromExecution), name="VirtualUsers-"+str(vUserId))
		t.daemon = True
		t.start()
		vUserId+=1

	numberOfExecutedScenarios=0

	with open(executionPlan) as execution:
		#logger.info("Running iteration: [%s] out of [%s]", it, iterationNumber)
		for executionDetails in execution:
			if executionDetails.startswith(COMMENTED_LINE):
				logger.info("Skipping scenario: %s", executionDetails)
				continue
			elif executionDetails.startswith(SINGLE_FOR):
				executionDetails = executionDetails.replace(SINGLE_FOR, "")
				logger.debug("Executing single job with details [%s].", executionDetails)
				scenario = support.ScenarioDefinition(executionDetails, scenariosConfiguration)
				scenarioToExecute.put(scenario)
				numberOfExecutedScenarios+=1
			elif executionDetails.startswith(BATCH_FOR):
				executionDetails = executionDetails.replace(BATCH_FOR, "")
				#LTE05ERBS|10.236.116.|60|1|3|add_node_scenario.cfg,sync_node_scenario.cfg
				config = executionDetails.split(DELIMITER)
				baseNodeName=config[0]
				baseNodeIp=config[1]
				startNumber=int(config[2])
				numberOfNodes=int(config[3])
				paddingUsedToFillWithCerosInName=config[4]
				scenarios=config[5]

				for nodeNumber in xrange(startNumber, (numberOfNodes + startNumber)):
					strNodeNumber=str(nodeNumber)
					executionDetailsCreated=baseNodeName + strNodeNumber.zfill(int(paddingUsedToFillWithCerosInName)) + DELIMITER + baseNodeIp + strNodeNumber + DELIMITER + scenarios
					#SINGLE_FOR:LTE05ERBS00001|10.236.116.1|add_node_scenario.cfg,sync_node_scenario.cfg
					logger.debug("Creating scenario for node [%s] up to [%s]. With details [%s].", strNodeNumber, str(numberOfNodes + startNumber), executionDetailsCreated)

					scenario = support.ScenarioDefinition(executionDetailsCreated, scenariosConfiguration)
					scenarioToExecute.put(scenario)
					numberOfExecutedScenarios+=1
			else:
				logger.error("ExecutionPlan [%s] was not processed.", executionPlan)


	scenarioToExecute.join()


	for i in xrange(numberOfExecutedScenarios):
		print str(resultsFromExecution.get()) + "\n"
	
	logger.info("Iteration completed")
	#sys.exit()

def printExecutionConfiguration():
	if not os.path.isfile(executionPlan):
		print "Execution Plan [",executionPlan,"] does not exist. Terminating execution."
		sys.exit()

	if not isUrlValid(enmUrl):
		sys.exit()

	print support.bcolors.BOLD+"Executing [",iterationNumber,"] time(s) scenarios with [",sleepTime,"] second(s) sleepTime. Using config file:"+support.bcolors.ENDC, executionPlan,"with",virtualUsers,"virtual users."
	print support.bcolors.BOLD+"Url used for cli:"+support.bcolors.ENDC,enmUrl
	print support.bcolors.BOLD+"Log file used:"+support.bcolors.ENDC,LOG_FILE_NAME
	logger.info('Starting ha testing')

def updateProgress(progress):
	sys.stdout.write("\rProgress at executing scenatios is %d%%" % progress)
	sys.stdout.flush() 
	if int(progress) >= 100:
		print "\n\n"


def isUrlValid(url):
	isValid=False
	req = urllib2.Request(url)
	try:
		resp = urllib2.urlopen(req, timeout=2)
		isValid = True
		logger.info("Cli Url is reachable [%s].",enmUrl)
	except:
		e = sys.exc_info()
		print "Cli Url is not reachable [",enmUrl,"]."
		logger.error("Cli Url is invalid [%s]. Exception: %s", url, str(e))
		isValid=False
	return isValid

def processEventFromQueueToExecuteScenario(executionQueue, resultsFromExecution):
	while True:
		executionTask = executionQueue.get()

		executionDetails = executionTask.getDetails()
		dictionaryWithScenarioDetails = executionTask.getConfig()

		logger.debug('Openning session to %s, with %s user', enmUrl, enmUser)
		try:
			session = enmscripting.open(enmUrl,enmUser,enmPass)
		except:
			logger.error("Session was not open on [%s].", enmUrl)
			executionQueue.task_done()
			break;
		executionTime=time.strftime("%d/%b/%Y %H:%M:%S")

		config = executionDetails.split(DELIMITER)
		nodeName=config[0]
		nodeIp=config[1]
		scenario=config[2].replace("\n","")
		steps=scenario.split(",")

		useCaseResultList = []

		scenarioName=""
		for scenarioStep in steps:
			try:
				if not scenarioName:
					scenarioName+=scenarioStep
				else:
					scenarioName+=" + " + scenarioStep
				logger.info('Working on %s', scenarioStep)
				useCaseResults = executeUseCase(session, scenarioStep, nodeName, nodeIp, executionTime, dictionaryWithScenarioDetails)
				useCaseResultList.append(useCaseResults)
			except support.TimeoutProblem,e:
				logger.error("Error: [%s].", str(e))
				break;
		enmscripting.close(session)

		result = support.ScenarioExecutionResults(executionTime, executionDetails, useCaseResultList, nodeName, current_thread().getName())

		resultsFromExecution.put(result)
		executionQueue.task_done()

		try:
			publishResults(scenarioName, result, nodeName, nodeIp, executionTime, useCaseResultList)
		except:
			e = sys.exc_info()
			logger.warn("Rest service is down [%s].", str(e))

		

def publishResults(scenarioName, result, nodeName, nodeIp, executionTime, useCaseResultList):
	totalSucesses=0
	totalFailures=0
	totalExecutionTime=0
	#print useCaseResultList
	for ucResults in useCaseResultList:
		totalSucesses+=ucResults.getSucessfuls()
		totalFailures+=ucResults.getFailures()
		totalExecutionTime+=ucResults.getTimeTaken()

	#print totalSucesses
	#print totalFailures
	# Invoke the rest save data
	scenarioName=scenarioName.replace("_scenario.cfg", "");
	payload = {"timeTaken" : totalExecutionTime, "startTime" : executionTime, "vuser":result.vuser, "nodeName":nodeName, "ipAddress":nodeIp, "ucName":scenarioName,  "successfulAssertions":totalSucesses, "failedAssertions":totalFailures,"useCases":[{"name": "add_node_scenario.cfg", "executionTime":"12", "successfulAssertions": "2", "failedAssertions":"2"}, {"name": "delete_node_scenario.cfg", "executionTime":"12", "successfulAssertions": "2", "failedAssertions":"2"}]}
	payload_json = json.dumps(payload)
	headers = {'Content-type': 'application/json'}
	r = requests.post(restService, data=payload_json, headers=headers)

def loadAllCfgScenariosIntoDictionary():
	configFiles = glob.glob("./*.cfg")
	dictionaryWithScenarioDetails=dict()
	for configFile in configFiles:
		logger.debug("Loading configuration from %s", configFile)
		with open(configFile) as cfgFile:
			fileName=cfgFile.name.replace("./","").strip()
			dictionaryWithScenarioDetails[fileName]=[]
			for lineInFile in cfgFile:
				dictionaryWithScenarioDetails[fileName].append(lineInFile)

	return dictionaryWithScenarioDetails

def executeUseCase(session, useCase, nodeName, ip, executionTime, dictionaryWithScenarioDetails):
	useCaseResults = support.UseCaseResults(useCase)
	useCaseResults.startTimer()
	for commandLine in dictionaryWithScenarioDetails[useCase]:
		commandLine = commandLine.replace("LTE_NODE_NAME", nodeName)
		commandLine = commandLine.replace("LTE_NODE_IP", ip)
		executeCliCommand(session, commandLine, useCaseResults, executionTime);
	useCaseResults.endTimer()
	return useCaseResults

def executeCliCommand(session, cliCommand, useCaseResults, executionTime):
	cliCommand=cliCommand.replace("\n","")
	logger.debug("%scliCommand [%s]%s", support.bcolors.OKBLUE, cliCommand, support.bcolors.ENDC)

	if cliCommand.startswith(WAIT_CONSTANT):
		fireCommandAndWait(session, cliCommand, useCaseResults, executionTime)
	else :
		fireCommand(session, cliCommand, useCaseResults, executionTime)
	return

def fireCommand(session, cliCommand, useCaseResults, executionTime) :
	commandToExecute=cliCommand
	cliCommandWithExpectedResult=["command","expectedValue"]
	expectedValueReturned=""
	response=0

	isCliCommand=True
	try:
		expressionsForRealCommands=[VALIDATE_CONST_VAL_IN_RESP, VALIDATE_VARIABLE_VAL_IN_RESP, STORE_LAST_LINE_FOR]
		for expression in expressionsForRealCommands:
			if cliCommand.startswith(expression):
				logger.debug("Using parser for [%s]", expression)
				parser = support.CommandLineParser(cliCommand, expression, DELIMITER)
				commandToExecute = parser.getCliCommandToExecute()
				expectedValueReturned = parser.getExpectedValue()
				isCliCommand=parser.isCliCommand()
				cliCommandWithExpectedResult[1]=expectedValueReturned

		if cliCommand.startswith(REPLACE_IN_STORED_VARIABLE):
			isCliCommand=False
			cliCommandWithExpectedResult=cliCommand.replace(REPLACE_IN_STORED_VARIABLE, "").split(DELIMITER)
			variableName=cliCommandWithExpectedResult[0]
			stringToReplace=cliCommandWithExpectedResult[1]
			replacementString=cliCommandWithExpectedResult[2]
			if replacementString == "EMPTY":
				replacementString=""
			logger.debug("Replacing [%s] with [%s] in [%s]",stringToReplace, replacementString, variableName)
			positionInDictionary=current_thread().getName() + variableName
			valueBefore=globalDictionaryForStoredValues[positionInDictionary]
			valueAfter=valueBefore.replace(stringToReplace, replacementString)
			logger.debug("Variable [%s] was updated from [%s] value to [%s]",variableName,valueBefore,valueAfter)
			globalDictionaryForStoredValues[positionInDictionary]=valueAfter

		if cliCommand.startswith(INCREMENT_STORED_VARIABLE):
			isCliCommand=False
			cliCommandWithExpectedResult=cliCommand.replace(INCREMENT_STORED_VARIABLE, "").split(DELIMITER)
			variableName=cliCommandWithExpectedResult[0]
			valueToIncrement=cliCommandWithExpectedResult[1]
			positionInDictionary=current_thread().getName() + variableName
			valueBefore=globalDictionaryForStoredValues[positionInDictionary]
			valueAfter=int(valueBefore)+int(valueToIncrement)
			logger.debug("Variable [%s] was increased by [%s] from [%s] value to [%s]",variableName,valueToIncrement,valueBefore,valueAfter)
			globalDictionaryForStoredValues[positionInDictionary]=valueAfter
		if cliCommand.startswith(DECREMENT_STORED_VARIABLE):
			isCliCommand=False
			cliCommandWithExpectedResult=cliCommand.replace(DECREMENT_STORED_VARIABLE, "").split(DELIMITER)
			variableName=cliCommandWithExpectedResult[0]
			valueToDecrement=cliCommandWithExpectedResult[1]
			positionInDictionary=current_thread().getName() + variableName
			valueBefore=globalDictionaryForStoredValues[positionInDictionary]
			valueAfter=int(valueBefore)-int(valueToDecrement)
			logger.debug("Variable [%s] was decreased by [%s] from [%s] value to [%s]",variableName,valueToDecrement,valueBefore,valueAfter)
			globalDictionaryForStoredValues[positionInDictionary]=valueAfter
		if cliCommand.startswith(APPEND_TO_STORED_VARIABLE):
			isCliCommand=False
			cliCommandWithExpectedResult=cliCommand.replace(APPEND_TO_STORED_VARIABLE, "").split(DELIMITER)
			variableName=cliCommandWithExpectedResult[0]
			valueToAppend=cliCommandWithExpectedResult[1]
			positionInDictionary=current_thread().getName() + variableName
			valueBefore=globalDictionaryForStoredValues[positionInDictionary]
			valueAfter=str(valueBefore)+valueToAppend
			logger.debug("Variable [%s] was modified to append [%s]. Changing value from [%s] to [%s]",variableName,valueToAppend,valueBefore,valueAfter)
			globalDictionaryForStoredValues[positionInDictionary]=valueAfter
		if cliCommand.startswith(VALIDATE_FIRST_LESSTHAN_SECOND_VAR):
			isCliCommand=False
			cliCommandWithExpectedResult=cliCommand.replace(VALIDATE_FIRST_LESSTHAN_SECOND_VAR, "").split(DELIMITER)
			firstVarName=cliCommandWithExpectedResult[0]
			secondVarName=cliCommandWithExpectedResult[1]
			firstVarPositionInDictionary=current_thread().getName() + firstVarName
			secondVarPositionInDictionary=current_thread().getName() + secondVarName
			validateFirstLessThanSecond(globalDictionaryForStoredValues[firstVarPositionInDictionary], globalDictionaryForStoredValues[secondVarPositionInDictionary], useCaseResults, executionTime)
	except:
		e = sys.exc_info()
		logger.error("Error executing command [%s]. Details are: [%s]", cliCommand, str(e))

#	if RANDOM_STR_VALUE_PER_DAY in commandToExecute:
#		strValue=time.strftime("%d-%m-%y")
#		commandToExecute.replace(RANDOM_STR_VALUE_PER_DAY, strValue)
	if isCliCommand:
		try:
			response = session.terminal().execute(commandToExecute, timeout_seconds=COMMAND_TIME_OUT)

			listOfResponses=[]
			for responseLine in response.get_output():
				if responseLine:
					logger.debug("%s", responseLine)
					listOfResponses.append(responseLine)
			lastLine = responseLine;
	
			useCaseResults.addCommandWithResponses(commandToExecute, listOfResponses)
	
			if cliCommand.startswith(VALIDATE_CONST_VAL_IN_RESP):
				expectedOutput=cliCommandWithExpectedResult[1]
				#assertTrue(lastLine, expectedOutput, useCaseResults)
				validateResponseContainsExpectedValueFor(listOfResponses, expectedOutput, useCaseResults, executionTime)
			if cliCommand.startswith(STORE_LAST_LINE_FOR):
				positionInDictionary=current_thread().getName() + cliCommandWithExpectedResult[1]
				globalDictionaryForStoredValues[positionInDictionary]=lastLine
				logger.debug("Storing [%s] in [%s]",lastLine,positionInDictionary)
			if cliCommand.startswith(VALIDATE_VARIABLE_VAL_IN_RESP):
				positionInDictionary=current_thread().getName() + cliCommandWithExpectedResult[1]
				expectedOutput=globalDictionaryForStoredValues[positionInDictionary]
				validateResponseContainsExpectedValueFor(listOfResponses, expectedOutput, useCaseResults, executionTime)
		except:
			e = sys.exc_info()
			logger.error("No response from cli for [%s]. Error: [%s]", cliCommand, str(e))

	return

def fireCommandAndWait(session, cliCommand, useCaseResults, executionTime) :
	cliCommandWithExpectedResult=cliCommand.replace(WAIT_CONSTANT, "").split(DELIMITER)
	command=cliCommandWithExpectedResult[0]
	result=cliCommandWithExpectedResult[1]
	configMaxNumOfRetries=cliCommandWithExpectedResult[2]
	configSleepTimeBtwnRetries=cliCommandWithExpectedResult[3]

	sucessfullWaitForCommand=False
	numberOfRetries=0
	while (sucessfullWaitForCommand==False) and (int(numberOfRetries) < int(configMaxNumOfRetries)):
		numberOfRetries += 1
		logger.debug("%s out of %s. Waiting for command [%s] to complete. Expecting result [%s]. Found: %s. Keep trying: %s", str(numberOfRetries), str(configMaxNumOfRetries), command, result, str(sucessfullWaitForCommand), str((int(numberOfRetries) < int(configMaxNumOfRetries))))
		time.sleep( float(configSleepTimeBtwnRetries) )

		try:
			response = session.terminal().execute(cliCommandWithExpectedResult[0])
		
			for responseLine in response.get_output():
				if responseLine:
					logger.debug("%s", responseLine)
					if cliCommandWithExpectedResult[1] in responseLine:
						sucessfullWaitForCommand=True
		except:
			e = sys.exc_info()
			logger.error("No response from cli for [%s]. Error: [%s]", cliCommand, str(e))

	if sucessfullWaitForCommand:
		logger.debug("Command was sucessful")
	else:
		logger.warn("Command unsucessful and timeout executed.")
		#raise support.TimeoutProblem("Command unsucessful and timeout executed!")
	return

def printResults(color, id, value):
	print color + id + " " + str(value) + support.bcolors.ENDC

def printCommand(command):
	print support.bcolors.OKBLUE + command + support.bcolors.ENDC

def printCommandResponse(command):
	print "\t"  + command 

def printLog(msg):
	print "\t" + support.bcolors.HEADER + msg + support.bcolors.ENDC

def printLogOk(msg):
	print "\t" + support.bcolors.OKGREEN + support.bcolors.BOLD + msg + support.bcolors.ENDC

def printLogError(msg):
	print "\t" + support.bcolors.WARNING + msg + support.bcolors.ENDC

def assertTrue(output, expected, useCaseResults, executionTime):
	name = useCaseResults.useCaseName
	if expected in output:
		logger.debug("%s[%s] was found in response.%s",support.bcolors.OKGREEN,expected,support.bcolors.ENDC)
		useCaseResults.incrementSucessfuls()
	else:
		logger.debug("%s[%s] was NOT found in response.%s",support.bcolors.WARNING,expected,support.bcolors.ENDC)
		useCaseResults.incrementFailures()

def validateFirstLessThanSecond(first, second, useCaseResults, executionTime):
	logger.debug("Validating first value [%s] is lower/equal than second value [%s].",first, second)
	first = int(first)
	second = int(second)
	if first<=second:
		logger.debug("%sFirst value [%s] is lower/equal than second value [%s].%s",support.bcolors.OKGREEN,first, second,support.bcolors.ENDC)
		useCaseResults.incrementSucessfuls()
	else:
		logger.error("%sSecond value [%s] is lower than first value [%s].%s",support.bcolors.WARNING,first, second,support.bcolors.ENDC)
		useCaseResults.incrementFailures()

def validateResponseContainsExpectedValueFor(outputList, expected, useCaseResults, executionTime):
	logger.debug("Validating expected value [%s] is in the response",expected)
	name = useCaseResults.useCaseName
	expectedFound=False
	for item in outputList:
		if expected in item:
			expectedFound=True
			break

	if expectedFound:
		logger.debug("%s[%s] was found in list of response.%s",support.bcolors.OKGREEN,expected,support.bcolors.ENDC)
		useCaseResults.incrementSucessfuls()
	else:
		logger.debug("%s[%s] was NOT found in list of response.%s",support.bcolors.WARNING,expected,support.bcolors.ENDC)
		useCaseResults.incrementFailures()

if __name__ == "__main__":
	setUpScript()

	for it in xrange(iterationNumber):
		logger.info("Running iteration [%s] out of [%s].", str(it), str(iterationNumber))
		main()
		time.sleep(sleepTime)
		logger.info("Sleeping now for [%s] until next execution.", sleepTime)
	logger.info("Execution finished!!")