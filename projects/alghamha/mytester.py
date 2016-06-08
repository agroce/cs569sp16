import sut
import random
import time
import sys
import os
import argparse

parser = argparse.ArgumentParser(description='My Tester, the argument must be specified in this order: "python mytester.py timeout seeds depth length FaultsEnabled CoverageEnabled RunningEnabled"')
parser.add_argument('-t','--timeout', type=int, nargs='?', default=60, help='Timeout will be parsed in seconds - The default value is 60 seconds')
parser.add_argument('-s','--seeds', type=int, nargs='?', default=0, help=' The number of seeds required. The default value is 0')
parser.add_argument('-d','--depth', type=int, nargs='?', default=100, help='The depth of each test case. The default is 100')
parser.add_argument('-l','--length', type=int, nargs='?', default=100, help='The length/Memory. The default value is 100')
parser.add_argument('-f','--FaultsEnabled', type=str, nargs='?', default='True', choices=['True', 'False'],  help='Save Test Case when Failure is discovered. The default value is True')
parser.add_argument('-c','--CoverageEnabled', type=str, nargs='?', default='True', choices=['True', 'False'], help='Report Code coverage. The default value is True')
parser.add_argument('-r','--RunningEnabled', type=str, nargs='?', default='True', choices=['True', 'False'], help='Check Coverage on the fly while running. The default value is True')
parser.add_argument('-a','--algorithm', type=str, nargs='?', default='prop', choices=['prop', 'grouping'], help='There are 2 Algorithms implemented here. The first is called [prop] that uses Random selections based on sepcified propability. The second Algorithm is called [grouping] that selects a group of actions and concentrate on this group using automatically assigned depths based on the length of enabled actions. The default algorithm is [prop]')
parser.add_argument('-p','--propertyCheck', type=str, nargs='?', default='False', choices=['True', 'False'], help='Check All properties defined in the SUT. The default Value is False')
parser.add_argument('-P','--Prop', type=float, nargs='?', default=0.5, help='Assign the propability that can be used for both algorithms. The default value is 0.5')

arguments = parser.parse_args()


# Terminate the program with time
# You can use 60 as a default Value
timeout = arguments.timeout

# Determines the random seed for testing. This should be assigned 0 when using the MEMORY/WIDTH
# You can use 12 as a default Value
seeds = arguments.seeds

# Tests Depth
# You can use 100 as a default Value
depth = arguments.depth

# MEMORY or Width, the number of "good" tests to store
# You can use a 100 as a default Value when testing combination lock faults
length = arguments.length

# Enable/Disable Faults
# You can use 1 as a default Value
# To save some string comparasion time
if arguments.FaultsEnabled == 'True':
	FaultsEnabled = 1
else:
	FaultsEnabled = 0

# Enable/Disable Coverage
# You can use 1 as a default Value
# To save some string comparasion time
if arguments.CoverageEnabled == 'True':
	CoverageEnabled = 1
else:
	CoverageEnabled = 0

# Enable/Disable Running
# You can use 1 as a default Value
# To save some string comparasion time
if arguments.RunningEnabled == 'True':
	RunningEnabled = 1
else:
	RunningEnabled = 0

# Type of Algorithm to be used in this testing
# You can use 0 for the radnom testing and 1 for the Group Random Testing
algorithm = arguments.algorithm

# Check the properties
# You can use 1 to enable this feature
# To save some string comparasion time
if arguments.propertyCheck == 'True':
	propertyCheck = 1
else:
	propertyCheck = 0

# Check the properties
# You can use 1 to enable this feature
Prop = arguments.Prop

# gloable variables initilization
sut = sut.sut()
sut.silenceCoverage()
bugs = 0
goodTests = []
startTime = time.time()

# Function To Save The Faults
def	saveFaults(bug, testCase):
	FileName = 'failure'+str(bug)+'.test'
	sut.saveTest(testCase,FileName)
	


# Combined Sequntial and Random tester algorithm 
if (algorithm == 'prop'):
	for act in sut.enabled():
		seq = sut.safely(act)
		if (not seq) and (FaultsEnabled == 1):
			#Sequential = "Discovered By Sequential Algorithm" 
			elapsedFailure = time.time() - startTime
			bugs += 1
			print "FOUND A FAILURE"
			print sut.failure()
			sut.prettyPrintTest(sut.test())
			test = sut.test()
			#Fault = sut.failure()
			saveFaults( bugs, test)
			sut.restart()
			# Print the new discovered branches	
		if (len(sut.newBranches()) > 0) and (RunningEnabled == 1):
			#print "sequential found this branch"
			print "ACTION:",act[0]
			elapsed1 = time.time() - startTime
			for b in sut.newBranches():
				print elapsed1,len(sut.allBranches()),"New branch",b
	sut.restart()
	rgen = random.Random(seeds)
	action = None
	# RandomTester based on randomly selcted propability
	while (time.time() - startTime <= timeout):
		# Based on propability replayback saved good tests those are saved when new branches got discovered. It is good for finding combanition luck faults
		if (len(goodTests) > 0) and (rgen.random() < Prop):
			sut.backtrack(rgen.choice(goodTests)[1])
			if (time.time() - startTime >= timeout):
				break
		else:
			sut.restart()

		# Based on the depth randomly execute an action
		for s in xrange(0,depth):
			if (time.time() - startTime >= timeout):
				break
			action = sut.randomEnabled(rgen)
			if (action == None):
				print "TERMINATING TEST DUE TO NO ENABLED ACTIONS"
				break
			r = sut.safely(action)
			# Start saving discovered fault on Disk
			if (not r) and (FaultsEnabled == 1):
				#RandomAlgorithm = "Discovered By Random Algorithm" 
				elapsedFailure = time.time() - startTime
				bugs += 1
				print "FOUND A FAILURE"
				print sut.failure()
				sut.prettyPrintTest(sut.test())
				test = sut.test()
				#Saving discovered fault on Disk
				saveFaults(bugs, test)
				# Rest the system state
				sut.restart()
			if (time.time() - startTime >= timeout):
				break
			# This part is for checking the property 
			if (propertyCheck == 1):
				checkResult = sut.check()
				if (not checkResult):
					bugs += 1
					print "FOUND A FAILURE"
					print sut.failure()
					sut.prettyPrintTest(sut.test())
					test = sut.test()
					#Saving discovered fault on Disk
					saveFaults(bugs, test)
					# Rest the system state
					sut.restart()
				if (time.time() - startTime >= timeout):
					break
			# Print the new discovered branches	
			if (len(sut.newBranches()) > 0) and (RunningEnabled == 1):
				#print "Random Found this branches"
				print "ACTION:",action[0]
				elapsed1 = time.time() - startTime
				for b in sut.newBranches():
					print elapsed1,len(sut.allBranches()),"New branch",b
			if (time.time() - startTime >= timeout):
				break
			# When getting new branches, save the test case into goodTest list to be re-executed based on random propability
			if ((length != 0) and ((len(sut.newBranches()) > 0) or (len(sut.newStatements()) > 0))):
				goodTests.append((sut.currBranches(), sut.state()))
				goodTests = sorted(goodTests, reverse=True, key = lambda x: len(x[0]))
			# Cleanup goodTest list based on the length of the goodTests
			if (length != 0) and (len(sut.newBranches()) == 0) and (len(goodTests) >= length):
				RandomMemebersSelection = random.sample(goodTests,int(float((len(goodTests))*.20)))
				for x in RandomMemebersSelection:
					goodTests.remove(x)

# This is the second grouping algorithm which groups actions together and testing them based on a given propability. The algorithm will randomly selects a group of actions and continue testing them based on the given propability, then based on a propability the saved good test cases (These test cases will be added to goodTests list based on new discovered branches ) will be replayed back from time to time.

elif (algorithm == 'grouping'):
	sut.restart()
	rgen = random.Random(seeds)
	action = None
	TimeElapsed = time.time()
	# RandomTester based on randomly selcted propability
	while (time.time() - startTime <= timeout):
		# Based on propability replayback saved good tests those are saved when new branches got discovered. It is good for finding combanition luck faults
		if (len(goodTests) > 0) and (rgen.random() < Prop):
			sut.backtrack(rgen.choice(goodTests)[1])
			if (time.time() - startTime >= timeout):
				break

			# Based on the depth execute an action randomly building on the previousely executed savedTest
			for s in xrange(0,depth):
				if (time.time() - startTime >= timeout):
					break

				action = sut.randomEnabled(rgen)
				if (action == None):
					print "TERMINATING TEST DUE TO NO ENABLED ACTIONS"
					break
				r = sut.safely(action)
				# Start saving discovered fault on Disk
				if (not r) and (FaultsEnabled == 1):
					print r
					#RandomAlgorithm = "Discovered By Random Algorithm" 
					elapsedFailure = time.time() - startTime
					bugs += 1
					print "FOUND A FAILURE"
					print sut.failure()
					sut.prettyPrintTest(sut.test())
					test = sut.test()
					#Saving discovered fault on Disk
					saveFaults(bugs, test)
					# Rest the system state
					sut.restart()
				if (time.time() - startTime >= timeout):
					break
				# This part is for checking the property 
				if (propertyCheck == 1):
					checkResult = sut.check()
					if (not checkResult):
						bugs += 1
						print "FOUND A FAILURE"
						print sut.failure()
						sut.prettyPrintTest(sut.test())
						test = sut.test()
						#Saving discovered fault on Disk
						saveFaults(bugs, test)
						# Rest the system state
						sut.restart()
					if (time.time() - startTime >= timeout):
						break
				# Print the new discovered branches	
				if (len(sut.newBranches()) > 0) and (RunningEnabled == 1):
					#print "Random Found this branches"
					print "ACTION:",action[0]
					elapsed1 = time.time() - startTime
					for b in sut.newBranches():
						print elapsed1,len(sut.allBranches()),"New branch",b
				if (time.time() - startTime >= timeout):
					break
				# When getting new branches, save the test case into goodTest list to be re-executed based on random propability
				if ((length != 0) and ((len(sut.newBranches()) > 0) or (len(sut.newStatements()) > 0))):
					goodTests.append((sut.currBranches(), sut.state()))
					goodTests = sorted(goodTests, reverse=True, key = lambda x: len(x[0]))
				# Cleanup goodTest list based on the length of the goodTests
				if (length != 0) and (len(sut.newBranches()) == 0) and (len(goodTests) >= length):
					RandomMemebersSelection = random.sample(goodTests,int(float((len(goodTests))*.20)))
					for x in RandomMemebersSelection:
						goodTests.remove(x)
			
		
		# This part will randomly selects a group of actions and continue testing them based on a given propability
		else:	
			sut.restart()
			# Select a group of action 
			groupActions = random.sample(sut.enabled(),int(len(sut.enabled())* Prop))
			# Calculate the length of groupActions and take some percentage to be the depth
			for s in xrange(0,int(len(groupActions) * Prop)):
				if (time.time() - startTime >= timeout):
					break
				# Use the actions them one by one 
				action = groupActions[s]
				
				if (action == None):
					print "TERMINATING TEST DUE TO NO ENABLED ACTIONS"
					break
				# Execute The actions one by one 
				r = sut.safely(action)
				# Start saving discovered fault on Disk
				if (not r) and (FaultsEnabled == 1):
					print r
					#RandomAlgorithm = "Discovered By Random Algorithm" 
					elapsedFailure = time.time() - startTime
					bugs += 1
					print "FOUND A FAILURE"
					print sut.failure()
					sut.prettyPrintTest(sut.test())
					test = sut.test()
					#Saving discovered fault on Disk
					saveFaults(bugs, test)
					# Rest the system state
					sut.restart()
				if (time.time() - startTime >= timeout):
					break
				# This part is for checking the property 
				if (propertyCheck == 1):
					checkResult = sut.check()
					if (not checkResult):
						bugs += 1
						print "FOUND A FAILURE"
						print sut.failure()
						sut.prettyPrintTest(sut.test())
						test = sut.test()
						#Saving discovered fault on Disk
						saveFaults(bugs, test)
						# Rest the system state
						sut.restart()
					if (time.time() - startTime >= timeout):
						break
				# Print the new discovered branches	
				if (len(sut.newBranches()) > 0) and (RunningEnabled == 1):
					#print "Random Found this branches"
					print "ACTION:",action[0]
					elapsed1 = time.time() - startTime
					for b in sut.newBranches():
						print elapsed1,len(sut.allBranches()),"New branch",b
				if (time.time() - startTime >= timeout):
					break
				# When getting new branches, save the test case into goodTest list to be re-executed based on random propability
				if ((length != 0) and ((len(sut.newBranches()) > 0) or (len(sut.newStatements()) > 0))):
					goodTests.append((sut.currBranches(), sut.state()))
					goodTests = sorted(goodTests, reverse=True, key = lambda x: len(x[0]))
				# Cleanup goodTest list based on the length of the goodTests
				if (length != 0) and (len(sut.newBranches()) == 0) and (len(goodTests) >= length):
					RandomMemebersSelection = random.sample(goodTests,int(float((len(goodTests))*.20)))
					for x in RandomMemebersSelection:
						goodTests.remove(x)

# Printing Report
elapsed = time.time() - startTime
print "\n                  ############ The Final Report ############# \n"
print elapsed, "Total Running Time"
print bugs, " Failures Found"
if (CoverageEnabled == 1):
	print len(sut.allBranches()),"BRANCHES COVERED"
	print len(sut.allStatements()),"STATEMENTS COVERED"
	sut.internalReport()




