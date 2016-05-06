import sut as sut
import random
import time
import sys
import os


# Terminate the program with time
TIMEOUT = int(sys.argv[1])

# Determines the random seed for testing
SEEDS = int(sys.argv[2])

# TEST_LENGTH or Depth
DEPTH = int(sys.argv[3])

# MEMORY or Width, the number of "good" tests to store
MEMORY = int(sys.argv[4])

# Enable/Disable Faults
FaultsEnabled = int(sys.argv[5])

# Enable/Disable Coverage
CoverageEnabled = int(sys.argv[6])

# Enable/Disable Running
RunningEnabled = int(sys.argv[7])


if (SEEDS > 0 ):
	rgen = random.Random(SEEDS)
else:
	rgen = random.Random(None)

sut = sut.sut()
sut.silenceCoverage()
bugs = 0
#sut.restart()
goodTests = []
startTime = time.time()
PopulationList = []

def	saveFaults(elapsedFailure, fault, act, bug, REDUCING):
	FileName = 'failure'+str(bug)+'.test'
	file = open(FileName, 'w+')
	print >> file, elapsedFailure, "Time it takes the tester to discover this fault \n"
	print >> file, fault, "\n"
	print >> file, " Reduced Test Case \n"	
	i = 0
	for s in REDUCING:
		steps = "# STEP " + str(i)
		print >> file, sut.prettyName(s[0]).ljust(80-len(steps),' '),steps
		i += 1
	file.close()
	print fault

startTime = time.time()



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

while (time.time() - startTime <= TIMEOUT):

	if (len(goodTests) > 0) and (rgen.random() < 0.5):
		sut.backtrack(rgen.choice(goodTests)[1])
	else:
		sut.restart()
	for s in xrange(0,DEPTH):
		
		action = sut.randomEnabled(rgen)
		r = sut.safely(action)
		if (not r) and (FaultsEnabled == 1):
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
			#sut.prettyPrintTest(sut.test())
			#print 
		if (len(sut.newBranches()) > 0) and (RunningEnabled == 1):
			print "ACTION:",action[0]
			elapsed1 = time.time() - startTime
			for b in sut.newBranches():
			#print time.time(),len(sut.allBranches()),'NEW BRANCHES:', sut.newBranches()
				print elapsed1,len(sut.allBranches()),"New branch",b
		
		if ((MEMORY != 0) and (len(sut.newBranches()) > 0)):
			goodTests.append((sut.currBranches(), sut.state()))
			goodTests = sorted(goodTests, reverse=True)[:MEMORY]
		elif (MEMORY != 0) and (len(sut.newBranches()) == 0) and (len(goodTests) >= MEMORY):
			RandomMemebersSelection = random.sample(goodTests,int(float((len(goodTests))*.20)))
			for x in RandomMemebersSelection:
				goodTests.remove(x)
			
	#print goodTests
# This is not working...........
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




