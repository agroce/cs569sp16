import sut
import random
import sys
import time


testsCovered = []

S= None
savedTest = None
failureCount = 0

TIME_BUDGET = int(sys.argv[1])

SEED = int(sys.argv[2])

DEPTH = int(sys.argv[3])

WIDTH = int(sys.argv[4])

FAULT_CHECK = int(sys.argv[5])

COVERAGE_REPORT = int(sys.argv[6])

RUNNING_DETAIL = int(sys.argv[7])

rgen = random.Random()
rgen.seed(SEED)

sut = sut.sut()
#sut.silenceCoverage()

start = time.time()
while time.time()-start < TIME_BUDGET:
    sut.restart()
    for s in xrange(0,DEPTH):
	action = sut.randomEnabled(rgen)
	if(RUNNING_DETAIL):	
        	elapsed = time.time() - start
		if sut.newBranches() != set([]):
			print "ACTION:",action[0]
			for b in sut.newBranches():
				print elapsed,len(sut.allBranches()),"New branch",b
        ok = sut.safely(action)	
	if (not ok):		
		S = sut.reduce(sut.test(), lambda x: sut.fails(x) or sut.failsCheck(x))			
		if S not in testsCovered:
			testsCovered.append(S)
			print "------------------------------------------"+ "\n"			
			print "Reduced Test"
			sut.prettyPrintTest(S)
			failureCount += 1
			if (FAULT_CHECK):
			    f = open("failure_file" + str(failureCount) + ".test", "w")
			    j = 0
		       	    for (s_reduces, _, _) in S:
				    steps_reduce = "# STEP " + str(j)
				    print >> f, sut.prettyName(s_reduces).ljust(80 - len(steps_reduce), ' '), steps_reduce
				    j += 1
			    f.close()
		else:
			print "------------------------------------------"+ "\n"	
			print "Same test"
			sut.prettyPrintTest(S)
			break;

                  

if (COVERAGE_REPORT):
    sut.internalReport()
