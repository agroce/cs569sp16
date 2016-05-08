import sut as sut
import random
import time
import sys
import os


# Terminate the program with time
# You can use 60 as a default Value
timeout = int(sys.argv[1])

# Determines the random seed for testing. This should be assigned 0 when using the MEMORY/WIDTH
# You can use 12 as a default Value
seeds = int(sys.argv[2])

# TEST_LENGTH or Depth
# You can use 100 as a default Value
depth = int(sys.argv[3])

# MEMORY or Width, the number of "good" tests to store
# You can use a 100 as a default Value when testing combination lock faults
length = int(sys.argv[4])

# Enable/Disable Faults
# You can use 1 as a default Value
FaultsEnabled = int(sys.argv[5])

# Enable/Disable Coverage
# You can use 1 as a default Value
CoverageEnabled = int(sys.argv[6])

# Enable/Disable Running
# You can use 1 as a default Value
RunningEnabled = int(sys.argv[7])

# gloable variables initilization
sut = sut.sut()

bugs = 0
goodTests = []
startTime = time.time()

# Function To Save The Faults
def	saveFaults(elapsedFailure, fault, act, bug, testCase, Algorithm):
	FileName = 'failure'+str(bug)+'.test'
	file = open(FileName, 'w+')
	print >> file, Algorithm
	print >> file, elapsedFailure, "Time it takes the tester to discover this fault \n"
	print >> file, fault, "\n"
	print >> file, " Test Case \n"	
	i = 0
	# Reading the test case as in randomester.py
	for s in testCase:
		steps = "# STEP " + str(i)
		print >> file, sut.prettyName(s[0]).ljust(80-len(steps),' '),steps
		i += 1
	file.close()
	print fault

# Sequntial algorithm that will traverse over all actions and execute them one by one

for act in sut.enabled():
	seq = sut.safely(act)
	if (not seq) and (FaultsEnabled == 1):
		Sequential = "Discovered By Sequential Algorithm" 
		elapsedFailure = time.time() - startTime
		bugs += 1
		print "FOUND A FAILURE"
		sut.prettyPrintTest(sut.test())
		test = sut.test()
		Fault = sut.failure()
		saveFaults(elapsedFailure, Fault, act, bugs, test, Sequential)
		sut.restart()
			# Print the new discovered branches	
	if (len(sut.newBranches()) > 0) and (RunningEnabled == 1):
		print "ACTION:",act[0]
		elapsed1 = time.time() - startTime
		for b in sut.newBranches():
			print elapsed1,len(sut.allBranches()),"New branch",b

rgen = random.Random(seeds)

# RandomTester based on randomly selcted propability
while (time.time() - startTime <= timeout):
	# This will work only Memory input is set. It is good for finding combanition luck faults
	if (len(goodTests) > 0) and (rgen.random() < 0.5):
		sut.backtrack(rgen.choice(goodTests)[1])
		if (time.time() - startTime >= timeout):
			break
	else:
		sut.restart()

	# Based on the depth randonly execute an action
	for s in xrange(0,depth):
		if (time.time() - startTime >= timeout):
			break
		action = sut.randomEnabled(rgen)
		r = sut.safely(action)
		# Start saving discovered fault on Disk
		if (not r) and (FaultsEnabled == 1):
			RandomAlgorithm = "Discovered By Random Algorithm" 
			elapsedFailure = time.time() - startTime
			bugs += 1
			print "FOUND A FAILURE"
			sut.prettyPrintTest(sut.test())
			test = sut.test()
			Fault = sut.failure()
			#Saving discovered fault on Disk
			saveFaults(elapsedFailure, Fault, action, bugs, test, RandomAlgorithm)
			# Rest the system state
			sut.restart()
		if (time.time() - startTime >= timeout):
			break
		# Print the new discovered branches	
		if (len(sut.newBranches()) > 0) and (RunningEnabled == 1):
			print "ACTION:",action[0]
			elapsed1 = time.time() - startTime
			for b in sut.newBranches():
				print elapsed1,len(sut.allBranches()),"New branch",b
		if (time.time() - startTime >= timeout):
			break
		# When getting new branches, save the test case into goodTest list to be executed based on random propability
		if ((length != 0) and (len(sut.newBranches()) > 0)):
			goodTests.append((sut.currBranches(), sut.state()))
			goodTests = sorted(goodTests, reverse=True)[:length]
		# Cleanup goodTest list based on the length of the goodTests
		elif (length != 0) and (len(sut.newBranches()) == 0) and (len(goodTests) >= length):
			RandomMemebersSelection = random.sample(goodTests,int(float((len(goodTests))*.20)))
			for x in RandomMemebersSelection:
				goodTests.remove(x)


# Printing Report
elapsed = time.time() - startTime
print "\n                  ############ The Final Report ############# \n"
print elapsed, "Total Running Time"
print bugs, " Bugs Found"
if CoverageEnabled == 1:
	print len(sut.allBranches()),"BRANCHES COVERED"
	print len(sut.allStatements()),"STATEMENTS COVERED"
	sut.internalReport()




