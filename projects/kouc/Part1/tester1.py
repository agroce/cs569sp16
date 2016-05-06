import sut as sut
import random
import time
import sys
import os


timeout = int (sys.argv[1])
seeds   = int (sys.argv[2])
depth   = int (sys.argv[3])
width  = int (sys.argv[4])
faultsEnabled = int(sys.argv[5])
coverageEnabled = int (sys.argv[6])
runningEnabled  = int(sys.argv[7])


if (seeds >0):
	rgen = random.Random(seeds)
else:
	rgen = random.Random(None)

sut = sut.sut
sut.silenceCoverage()
bugs =0
goodTest = []
startTime = time.time

def writeFaults(elapsedFailure,faults,act,bugs,REDUCING):
	global count 
	if faults:
		count+=1
		f_file = name
		f1=''
		for i in range(len(R)):
			f1=f1+R[i][0]+'\n'
		with open(f_file,'a') as f:
			if not phase:
				f.write('\nFaults found in random test phase:\n')
			else:
				f.write('\nFaults found in bfs test phase:\n')
			f.write('\n'+str(count)+':-------\n'+str(f1)+'\n')
			f.write(str(f2)+'\n')

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

while (time.time() - startTime <= timeout):
	
	if (len(goodTests) > 0) and (rgen.random() < 0.5):
		sut.backtrack(rgen.choice(goodTests)[1])
	else:
		sut.restart()
	
	for s in xrange(0,depth):
		action = sut.randomEnabled(rgen)
		r = sut.safely(action)

		if (not r) and (faultsEnabled == 1):
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
		
		if (len(sut.newBranches()) > 0) and (runningEnabled == 1):
			print "ACTION:",action[0]
			elapsed1 = time.time() - startTime
			for b in sut.newBranches():
				print elapsed1,len(sut.allBranches()),"New branch",b
		
		if ((width != 0) and (len(sut.newBranches()) > 0)):
			goodTests.append((sut.currBranches(), sut.state()))
			goodTests = sorted(goodTests, reverse=True)[:width]
		
		elif (width!= 0) and (len(sut.newBranches()) == 0) and (len(goodTests) >= width):
			RandomMemebersSelection = random.sample(goodTests,int(float((len(goodTests))*.20)))
			for x in RandomMemebersSelection:
				goodTests.remove(x)

elapsed = time.time() - startTime
print "\n                  ############ The Final Report ############# \n"
print elapsed, "Total Running Time"
print bugs, " Bugs Found"
if coverageEnabled == 1:
	CoverageFileName = 'coverage.out'
	sut.report(CoverageFileName)
	print "Coverage Report is Saved on Disk"
	print len(sut.allBranches()),"BRANCHES COVERED"
	print len(sut.allStatements()),"STATEMENTS COVERED"

