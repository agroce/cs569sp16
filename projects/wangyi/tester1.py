import sut
import random
import sys
import time

global belowMean, lastAddCoverage, actCount, bugs, failPool

TIMEOUT  = int(sys.argv[1])
SEED     = int(sys.argv[2])
DEPTH    = int(sys.argv[3])
WIDTH    = int(sys.argv[4])
FAULTS   = int(sys.argv[5])
COVERAGE = int(sys.argv[6])
RUNNING  = int(sys.argv[7])

def collectCoverage():
    global coverageCount
    for p in sut.currStatements():
        if p not in coverageCount:
            coverageCount[p] = 0
        coverageCount[p] += 1  

def randomAction():
    act = sut.randomEnabled(random.Random(SEED))
    actCount += 1
    ok = sut.safely(act)
    if not ok:
        bugs += 1
        print "FOUND A FAILURE"
        print sut.failure()
        print "REDUCING"
        failPool.append(sut.test())
        collectCoverage()
        R = sut.reduce(sut.test(),sut.fails, True, True)
        sut.prettyPrintTest(R)
        print sut.failure()
        sut.restart()
    else:
         if len(sut.newStatements()) != 0:
            oldTest = list(sut.test())
            storeTest = sut.reduce(oldTest,sut.coversStatements(sut.newStatements()))
            fullPool.append((storeTest, set(sut.currStatements())))
            lastAddCoverage = set(sut.currStatements())
         for p in belowMean:
            if p in sut.currStatements() and p not in lastAddCoverage:
            print "NEW PATH TO LOW COVERAGE STATEMENT",p
            fullPool.append((list(sut.test()), set(sut.currStatements())))
            lastAddCoverage = set(sut.currStatements())
            return
    return ok     

def buildActivePool():
    global activePool
    activePool = []
    for (t,c) in fullPool:
        for s in c:
            if s in belowMean:
                activePool.append((t,c))
                break
    print len(activePool),"TESTS IN THE ACTIVE POOL,",len(fullPool),"IN FULL POOL"      

explore = 0.7
actCount = 0
tests = []
coverageCount = {}
sut = sut.sut()
fail = []
bugs = 0
activePool = []
fullPool = []
failPool = []
belowMean = set([])

print "STARTING PHASE 1"

start = time.time()
ntests = 0
while time.time()-start < int(TIMEOUT):
    sut.restart()
    ntests += 1
    for s in xrange(0,DEPTH):
        if not randomAction():
            break 
    for s in sut.currStatements():
        if s not in coverage:
                coverage[s] = 0
        else coverage[s] += 1
printCoverage()
print "STARTING PHASE 2"

start = time.time()
while time.time()-start < int(TIMEOUT):
    buildActivePool()
    lastAddCoverage = set([])
    sut.restart()
    if rgen.random() > explore:
        exploitPool()
        lastAddCoverage = set(sut.currStatements()) 
    ntests += 1
    for s in xrange(0,DEPTH):
        if not randomAction():
            break
     

#sut.internalReport()


print ntests,"TESTS"


for (t,s) in fullPool:
    print len(t),len(s)

if coverage:
    sut.internalReport()

print bugs,"FAILED"
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-start
