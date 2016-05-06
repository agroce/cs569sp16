import sut
import random
import sys
import time
import math


TIMEOUT  = int(sys.argv[1])
SEED     = int(sys.argv[2])
DEPTH    = int(sys.argv[3])
WIDTH    = int(sys.argv[4])
FAULTS   = int(sys.argv[5])
COVERAGE = int(sys.argv[6])
RUNNING  = int(sys.argv[7])

#global variables are defined here
sut=sut.sut()
sut.silenceCoverage()
rgen = random.Random()
rgen.seed(SEED)

actCount = 0

bugs = 0
coverage = {}
bugQueue = []
newQueue = []




def randomAction():
    global actCount, bugs, bugQueue
    act = sut.randomEnabled(rgen)
    actCount += 1
    ok = sut.safely(act)
    if not ok:
        bugs += 1
        print "FOUND A FAILURE"
        print sut.failure()
        print "REDUCING"
        bugQueue.append(sut.test())
        collectCoverage()
        R = sut.reduce(sut.test(),sut.fails, True, True)
        sut.prettyPrintTest(R)
        print sut.failure()
        sut.restart()
    else:
    	#Find the new Statements
        if len(sut.newStatements()) != 0:
        	visited = list(sut.test())
        	test = sut.reduce(visited, sut.coversStatements(sut.newStatements()))
        	sut.replay(visited)
        	newQueue.append((test,set(sut.currStatements())))
    return ok  



def buildQueue():
	global activePool, belowMedian

	belowMedian = set([])

	visitedQueue = sorted(coverage.keys(), key = lambda x: coverage[x])

	t = visitedQueue[len(coverage) / 2]
	coverMedian = coverage[t]

	for s in visitedQueue:
		if coverage[s] < coverMedian:
			belowMedian.add(s)
		else:
			break

	newBelowMedian = set([])

	coverSum = sum(map(lambda x:coverage[x],belowMedian))
	coverMedian = coverSum / (1.0*len(belowMedian))
	for s in belowMedian:
		if coverage[s]<coverMedian:
			newBelowMedian.add(s)
	print len(newBelowMedian),"STATEMENTS BELOW MEDIAN BELOW MEDIAN COVERAGE OUT OF", len(belowMedian)
	belowMedian = newBelowMedian
	activePool = []
	for (t,c) in newQueue:
		for s in c:
			if s in belowMedian:
				activePool.append((t,c))
				break

print "STARTING PHASE 1"


start = time.time()

while(time.time() - start < TIMEOUT * 0.5):
    sut.restart()
    for s in xrange(0,DEPTH):
    	if not randomAction():
    		break
    for s in sut.currStatements():
   		if s not in coverage:
   			coverage[s] = 0
   		coverage[s] += 1



print "STARTING PHASE 2"


start2 = time.time()
while time.time() - start2 < TIMEOUT * 0.5:
	buildQueue()
	cover = set([])
	sut.restart()
	# if rgen.random() > 0.7:
	# 	sut.replay(rgen.choice(activePool)[0])
	# 	cover = set(sut.currStatements())
	for s in xrange(0, DEPTH):
		if not randomAction():
			break
	for s in sut.currStatements():
   		if s not in coverage:
   			coverage[s] = 0
   		coverage[s] += 1


sut.internalReport()

print bugs, "FAILED"
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-start





        

