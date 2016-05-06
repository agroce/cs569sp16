import sut as sut
import random
import time
import sys
import os


# Terminate the program with time
# You can use 60 as a default Value
TIMEOUT = int(sys.argv[1])

# Determines the random seed for testing. This should be assigned 0 when using the MEMORY/WIDTH
# You can use 12 as a default Value
SEEDS = int(sys.argv[2])

# TEST_LENGTH or Depth
# You can use 100 as a default Value
DEPTH = int(sys.argv[3])

# MEMORY or Width, the number of "good" tests to store
# You can use a 100 as a default Value when testing combination lock faults
MEMORY = int(sys.argv[4])

# Enable/Disable Faults
# You can use 1 as a default Value
FaultsEnabled = int(sys.argv[5])

# Enable/Disable Coverage
# You can use 1 as a default Value
CoverageEnabled = int(sys.argv[6])

# Enable/Disable Running
# You can use 1 as a default Value
RunningEnabled = int(sys.argv[7])


if (SEEDS > 0 ):
	rgen = random.Random(SEEDS)
else:
	rgen = random.Random(None)

# gloable variables initilization
sut = sut.sut()
sut.silenceCoverage()
bugs = 0
goodTests = []
startTime = time.time()

# Function To Save The Faults
def	saveFaults(elapsedFailure, fault, act, bug, REDUCING):
	FileName = 'failure'+str(bug)+'.test'
	file = open(FileName, 'w+')
	print >> file, elapsedFailure, "Time it takes the tester to discover this fault \n"
	print >> file, fault, "\n"
	print >> file, " Reduced Test Case \n"	
	i = 0
	# Reducing the Test Case
	for s in REDUCING:
		steps = "# STEP " + str(i)
		print >> file, sut.prettyName(s[0]).ljust(80-len(steps),' '),steps
		i += 1
	file.close()
	print fault

# Sequntial algorithm that will traverse over all actions and execute them one by one
for act in sut.enabled():
	seq = sut.safely(act)
	if (not seq) and (FaultEnabled == 1):
		elapsedFailure = time.time() - startTime
		bugs += 1
		print "FOUND A FAILURE"
		sut.prettyPrintTest(sut.test())
		test = sut.test()
		Fault = sut.failure()
		print "REDUCING"
		REDUCING = sut.reduce(sut.test(),sut.fails, True, True)
		sut.prettyPrintTest(REDUCING)
		saveFaults(elapsedFailure, Fault, act, bugs, REDUCING)
		sut.restart()

# RandomTester based on randomly selcted propability
while (time.time() - startTime <= TIMEOUT):
	# This will work only Memory input is set. It is good for finding combanition luck faults
	if (len(goodTests) > 0) and (rgen.random() < 0.5):
		sut.backtrack(rgen.choice(goodTests)[1])
	else:
		sut.restart()
	# Based on the depth randonly execute an action
	for s in xrange(0,DEPTH):
		action = sut.randomEnabled(rgen)
		r = sut.safely(action)
		# Start saving discovered fault on Disk
		if (not r) and (FaultsEnabled == 1):
			elapsedFailure = time.time() - startTime
			bugs += 1
			print "FOUND A FAILURE"
			sut.prettyPrintTest(sut.test())
			test = sut.test()
			Fault = sut.failure()
			# Start Reducing the Test Case
			print "REDUCING"
			REDUCING = sut.reduce(sut.test(),sut.fails, True, True)
			sut.prettyPrintTest(REDUCING)
			#Saving discovered fault on Disk
			saveFaults(elapsedFailure, Fault, act, bugs, REDUCING)
			# Rest the system state
			sut.restart()
		# Print the new discovered branches	
		if (len(sut.newBranches()) > 0) and (RunningEnabled == 1):
			print "ACTION:",action[0]
			elapsed1 = time.time() - startTime
			for b in sut.newBranches():
				print elapsed1,len(sut.allBranches()),"New branch",b
		# When getting new branches, save the test case into goodTest list to be executed based on random propability
		if ((MEMORY != 0) and (len(sut.newBranches()) > 0)):
			goodTests.append((sut.currBranches(), sut.state()))
			goodTests = sorted(goodTests, reverse=True)[:MEMORY]
		# Cleanup goodTest list based on the length of the goodTests
		elif (MEMORY != 0) and (len(sut.newBranches()) == 0) and (len(goodTests) >= MEMORY):
			RandomMemebersSelection = random.sample(goodTests,int(float((len(goodTests))*.20)))
			for x in RandomMemebersSelection:
				goodTests.remove(x)
# Printing Report
elapsed = time.time() - startTime
print "\n                  ############ The Final Report ############# \n"
print elapsed, "Total Running Time"
print bugs, " Bugs Found"
if CoverageEnabled == 1:
	CoverageFileName = 'coverage.out'
	sut.report(CoverageFileName)
	print "Coverage Report is Saved on Disk"
	print len(sut.allBranches()),"BRANCHES COVERED"
	print len(sut.allStatements()),"STATEMENTS COVERED"




