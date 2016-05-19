import sut
import random
import sys
import time
import os

BUDGET          = int(sys.argv[1])
SEED            = int(sys.argv[2])
depth           = int(sys.argv[3])
width           = int(sys.argv[4])
faults          = int(sys.argv[5])
coverage_report = int(sys.argv[6])
running         = int(sys.argv[7])

factor          = 0.5

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
    global actCount, bugs, failPool, faults, start
    restored = sys.stdout
    act = sut.randomEnabled(rgen)
    actCount += 1
    ok = sut.safely(act)
    elapsed = time.time() - start
    if running:
        if len(sut.newBranches()) > 0:
            print "ACTION:", act[0]
            for branch in sut.newBranches():
                print elapsed, len(sut.allBranches()), "New branch", branch

    if not ok:
        bugs += 1
        print "FOUND A FAILURE, REDUCING..."
        failPool.append(sut.test())
        collectCoverage()
        R = sut.reduce(sut.test(),sut.fails, True, True)

        if faults:
            print "SAVING INTO FILE NAMED failurefile"+str(bugs)
            sys.stdout = open(("failurefile" + str(actCount) + ".test"), 'w')
            sut.prettyPrintTest(R)
            sys.stdout.close()
            sys.stdout = restored

        sut.restart()
    else:
        expandPool()
    return ok

def findBelowMean():
    global belowMean

    belowMean = set([])
    sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])

    coverSum = sum(coverageCount.values())
    if len(coverageCount) == 0:
        coverMean = coverSum
    else:
        coverMean = coverSum / (factor*len(coverageCount))  
    for s in sortedCov:
        if coverageCount[s] < coverMean:
            belowMean.add(s)
        else:
            break
    print len(belowMean),"STATEMENTS BELOW MEAN COVERAGE OUT OF",len(coverageCount)
    newBelowMean = set([])
    coverSum = sum(map(lambda x:coverageCount[x],belowMean))
    if len(coverageCount) == 0:
        coverMean = coverSum
    else:
        coverMean = coverSum / (factor*len(coverageCount))  
    for s in belowMean:
        if coverageCount[s] < coverMean:
            newBelowMean.add(s)
    print len(newBelowMean),"STATEMENTS BELOW MEAN BELOW MEAN COVERAGE OUT OF",len(belowMean)
    belowMean = newBelowMean

def printCoverage():
    sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])

    coverSum = sum(coverageCount.values())
    if len(coverageCount) == 0:
        coverMean = coverSum
    else:
        coverMean = coverSum / (factor*len(coverageCount))  
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
    if activePool != []:
        sut.replay(rgen.choice(activePool)[0])
    else:
        sut.replay(rgen.choice(fullPool)[0])


rgen = random.Random()
rgen.seed(SEED)

explore = 0.7

actCount = 0

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
while time.time()-start < BUDGET / 2:
    sut.restart()
    ntests += 1
    for w in xrange(0, width):
        for s in xrange(0,depth):
            if not randomAction():
                break
    collectCoverage()

printCoverage()
print "STARTING PHASE 2"

start = time.time()
while time.time()-start < BUDGET / 2:
    buildActivePool()
    lastAddCoverage = set([])
    sut.restart()
    if rgen.random() > explore:
        exploitPool()
        lastAddCoverage = set(sut.currStatements())
    ntests += 1
    for w in xrange(0, width):
        for s in xrange(0,depth):
            if not randomAction():
                break
    collectCoverage()

if coverage_report:
    sut.internalReport()
    sut.report("coverage_report.txt")
    if not os.path.isdir("html"):
        os.mkdir("html")
    
    sut.htmlReport("./html")


print ntests,"TESTS"


for (t,s) in fullPool:
    print len(t),len(s)


print bugs,"FAILED"
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-start

