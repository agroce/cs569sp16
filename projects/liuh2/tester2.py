import sys
import random
import sut
import time



BUDGET  = int(sys.argv[1])
SEED 	 = int(sys.argv[2])
Depth 	 = int(sys.argv[3])
Width  	 = int(sys.argv[4])
faults   = int(sys.argv[5])
coverage_report = int(sys.argv[6])
Running  = int(sys.argv[7])



rgen = random.Random()
rgen.seed(SEED)

sut = sut.sut()

start = time.time()


bugs = 0

acts = 0

coverage_reportCount = {}
activePool = []
fullPool = []
belowMean = set([])
explore = 0.7



def collectcoverage_report():
    global coverage_reportCount
    for s in sut.currStatements():
        if s not in coverage_reportCount:
            coverage_reportCount[s] = 0
        coverage_reportCount[s] += 1 

def findBelowMean():
    global belowMean

    belowMean = set([])
    sortedCov = sorted(coverage_reportCount.keys(), key=lambda x: coverage_reportCount[x])

    coverSum = sum(coverage_reportCount.values())
    coverMean = coverSum / (1.0*len(coverage_reportCount))
  
    for s in sortedCov:   	
        if coverage_reportCount[s] < coverMean:
            belowMean.add(s)
        else:
            break

def buildActivePool():
    global activePool
    findBelowMean()
    activePool = []
    for (t,c) in fullPool:
        for s in c:
            if s in belowMean:
                activePool.append((t,c))
                break 



while time.time() - start < BUDGET/5 :
	sut.restart()
	for t in xrange(0,Depth):
		if time.time() - start > BUDGET:
			break
		act = sut.randomEnabled(rgen)
		ok  = sut.safely(act)
		collectcoverage_report()
		if len(sut.newStatements()) != 0:
			fullPool.append((list(sut.test()), set(sut.currStatements())))
		if not ok :
			bugs += 1
			if faults :
				
				print "Found faults",bugs, ": \n", sut.failure()
				filename = "failure" + str(bugs) + ".test"
				sut.saveTest(sut.test(),filename)
				
			break
		if Running :

			if sut.newBranches() != set([]):
				print "ACTION:", act[0]
				elapsed = time.time() - start
				for b in sut.newBranches():
					print elapsed,len(sut.allBranches()),"New branch",b
	collectcoverage_report()

 
while time.time() - start < BUDGET :
	if time.time() - start > BUDGET:
		break
	buildActivePool()
	sut.restart()
	for t in xrange(0,Depth):
		if time.time() - start > BUDGET:
			break
		act = sut.randomEnabled(rgen)
		ok  = sut.safely(act)
		if rgen.random() > explore:
			sut.replay(rgen.choice(activePool)[0])
		if Running :
			if sut.newBranches() != set([]):
				print "ACTION:", act[0]
				elapsed = time.time() - start
				for b in sut.newBranches():
					print elapsed,len(sut.allBranches()),"New branch",b
		
		acts += 1
		collectcoverage_report()
		if not ok :
			bugs += 1
			
			if faults :
				
				print "Found faults",bugs, ": \n", sut.failure()
				filename = "failure" + str(bugs) + ".test"
				sut.saveTest(sut.test(),filename)
				
			break
		
	collectcoverage_report()
if coverage_report :
	sut.internalReport()
print  bugs, "FAILED"
print "ACTIONS  : ", acts
print "RUN TIME : ", time.time() - start