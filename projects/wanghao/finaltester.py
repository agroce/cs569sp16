import sut
import random
import sys
import time

timeout = int(sys.argv[1])
seed = int(sys.argv[2])
depth = int(sys.argv[3])
width = int(sys.argv[4])
faults = int(sys.argv[5])
coverage = int(sys.argv[6])
running  = int(sys.argv[7])

def expandPool():
    global belowMean,lastAddCoverage,nonerrCount
    if len(sut.newStatements()) != 0:
        print "NEW STATEMENTS DISCOVERED",sut.newStatements()
        nonerrCount += 1
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

def randomAction():   
    global actCount, bugs, fails, errCount, newCount
    sawNew = False
    act = sut.randomEnabled(seeds)
    actCount += 1
    ok = sut.safely(act)
    propok = sut.check()
   
    if running:
        if sut.newBranches() != set([]):
            for b in sut.newBranches():
                print time.time()-start,len(sut.allBranches()),"New branch",b
            sawNew = True
            newCount += 1
        else:
            sawNew = False    

    if not ok or not propok:
        if faults:
            bugs += 1
            fail.append(sut.test())
            saveCover()
            R = sut.reduce(sut.test(),sut.fails, True, True)
            sut.restart()
            print "FAILURE FOUND.....FAILURES ARE STORING IN FILES"
            errCount += 1
            fault = sut.failure()
            fname = 'failure' + str(bugs) + '.test'
            sut.saveTest(sut.test(), fname)
            sut.restart() 

    else:
        expandPool()
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
    
def saveCover():
    global covCount
    for b in sut.currBranches():
        if b not in covCount:
            covCount[b] = 0
        covCount[b] += 1
        
def collectCoverage():
    global coverageCount
    for s in sut.currStatements():
        if s not in coverageCount:
            coverageCount[s] = 0
        coverageCount[s] += 1
        
def printCoverage():
    sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])

    coverSum = sum(coverageCount.values())
    coverMean = coverSum / (1.0*len(coverageCount))
    print "MEAN COVERAGE IS",coverMean
    for s in sortedCov:
        print s, coverageCount[s]
        
def exploitPool():
    sut.replay(rgen.choice(activePool)[0])

explore = 0.7
actCount = 0
tests = []
sut = sut.sut()
fail = []
covCount = {}
bugs = 0
seeds = random.Random(seed)
coverageCount = {}
activePool = []
fullPool = []
failPool = []
errCount = 0
nonerrCount = 0
newCount = 0

belowMean = set([])

print "STARTING PHASE 1"

start = time.time()
ntests = 0
while time.time() - start < timeout/2 - 1:
    if time.time() - start > timeout/2 - 1:
        break
    sut.restart()
    ntests += 1
    for s in xrange(0,depth):
        if not randomAction():
            break
    for s in sut.currStatements():
        if s not in coverageCount:
            coverageCount[s] = 0
        coverageCount[s] += 1

print "STARTING PHASE 2"

start = time.time()
while time.time() - start < timeout/2 - 1:
    if time.time() - start > timeout/2 - 1:
        break
    buildActivePool()
    lastAddCoverage = set([])
    sut.restart()
    #if random.Random().random() > explore:
    #    sut.replay(random.Random().choice(activePool)[0])
    #    lastAddCoverage = set(sut.currStatements())
    ntests += 1
    for s in xrange(0,depth):
        if not randomAction():
            break


print ntests,"TESTS"


for (t,s) in fullPool:
    print len(t),len(s)

if coverage:
    sut.internalReport()

print bugs,"FAILED"
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-start

