import sut
import random
import sys
import time

def collectCoverage():
    global coverageCount
    for s in sut.currStatements():
        if s not in coverageCount:
            coverageCount[s] = 0
        coverageCount[s] += 1    

def expandPool():
    global belowMean,lastAddCoverage 
    if len(sut.newStatements()) != 0:
        print "NEW STATEMENTS DISCOVERED",sut.newStatements()
        oldTest = list(sut.test())
        storeTest = sut.reduce(oldTest,sut.coversStatements(sut.newStatements()))
        print "OLD LENGTH = ",len(oldTest),"NEW LENGTH = ",len(storeTest)
        sut.replay(oldTest)
        fullPool.append((storeTest, set(sut.currStatements())))
        lastAddCoverage = set(sut.currStatements())
        return
    for s in belowMean:
        if s in sut.currStatements() and s not in lastAddCoverage:
            print "NEW PATH TO LOW COVERAGE STATEMENT",s
            fullPool.append((list(sut.test()), set(sut.currStatements())))
            lastAddCoverage = set(sut.currStatements())
            return

def randomAction():
    global actCount, bugs, failPool
    act = sut.randomEnabled(rgen)
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
        expandPool()
    return ok     

def findBelowMean():
    global belowMean

    belowMean = set([])
    sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])

    coverSum = sum(coverageCount.values())
    coverMean = coverSum / (1.0*len(coverageCount))
    for s in sortedCov:
        if coverageCount[s] < coverMean:
            belowMean.add(s)
        else:
            break
    print len(belowMean),"STATEMENTS BELOW MEAN COVERAGE OUT OF",len(coverageCount)
    newBelowMean = set([])
    coverSum = sum(map(lambda x:coverageCount[x],belowMean))
    coverMean = coverSum / (1.0*len(belowMean))
    for s in belowMean:
        if coverageCount[s] < coverMean:
            newBelowMean.add(s)
    print len(newBelowMean),"STATEMENTS BELOW MEAN BELOW MEAN COVERAGE OUT OF",len(belowMean)
    belowMean = newBelowMean
        

def printCoverage():
    sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])

    coverSum = sum(coverageCount.values())
    coverMean = coverSum / (1.0*len(coverageCount))
    print "MEAN COVERAGE IS",coverMean
    for s in sortedCov:
        print s, coverageCount[s]

def buildActivePool():
    global activePool
    findBelowMean()
    activePool = []
    for (t,c) in fullPool:
        for s in c:
            if s in belowMean:
                activePool.append((t,c))
                break
    print len(activePool),"TESTS IN THE ACTIVE POOL,",len(fullPool),"IN FULL POOL"        

def exploitPool():
    sut.replay(rgen.choice(activePool)[0])

rgen = random.Random()
depth = 100

explore = 0.7

actCount = 0
BUDGET1 = int(sys.argv[1])
BUDGET2 = int(sys.argv[2])

sut = sut.sut()

bugs = 0

coverageCount = {}
activePool = []
fullPool = []
failPool = []

belowMean = set([])

print "STARTING PHASE 1"

start = time.time()
ntests = 0
while time.time()-start < BUDGET1:
    sut.restart()
    ntests += 1
    for s in xrange(0,depth):
        if not randomAction():
            break
    collectCoverage()    

printCoverage()
print "STARTING PHASE 2"

start = time.time()
while time.time()-start < BUDGET2:
    buildActivePool()
    lastAddCoverage = set([])
    sut.restart()
    if rgen.random() > explore:
        exploitPool()
        lastAddCoverage = set(sut.currStatements()) 
    ntests += 1
    for s in xrange(0,depth):
        if not randomAction():
            break
    collectCoverage()    

#sut.internalReport()
printCoverage()

print ntests,"TESTS"


for (t,s) in fullPool:
    print len(t),len(s)


print bugs,"FAILED"
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-start
