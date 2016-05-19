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

def failure():
    global bugs, failPool
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
    return     

def newStatement():
    global lastAddCoverage
    print "NEW STATEMENTS DISCOVERED",sut.newStatements()
    oldTest = list(sut.test())
    storeTest = sut.reduce(oldTest,sut.coversStatements(sut.newStatements()))
    print "OLD LENGTH = ",len(oldTest),"NEW LENGTH = ",len(storeTest)
    sut.replay(oldTest)
    fullPool.append((storeTest, set(sut.currStatements())))
    lastAddCoverage = set(sut.currStatements())
    return

TIME = int(sys.argv[1])
SEED = int(sys.argv[2])
DEPTH = int(sys.argv[3])
WIDTH = int(sys.argv[4])
FAULT = int(sys.argv[5])
COVERAGE = int(sys.argv[6])
RUNNING = int(sys.argv[7])

rgen = random.Random()
rgen.seed(SEED)
actCount = 0
sut = sut.sut()
bugs = 0
coverageCount = {}
fullPool = []
failPool = []
belowMean = set([])
start = time.time()
ntests = 0

while time.time() - start < TIME:
    sut.restart()
    ntests += 1
    for s in xrange(0, DEPTH):
        actCount += 1
        act = sut.randomEnabled(rgen)
        ok = sut.safely(act)
        if RUNNING == 1:
            if len(sut.newBranches()) > 0:
                print "ACTION:", act[0]
                for b in sut.newBranches():
                    print time.time() - start, len(sut.allBranches()), "Newbranch", b
        if not ok:
            failure()
            break
        else:
            if len(sut.newStatements()) != 0:
                newStatement()

            for s in belowMean:
                if s in sut.currStatements() and s not in lastAddCoverage:
                    print "NEW PATH TO LOW COVERAGE STATEMENT",s
                    fullPool.append((list(sut.test()), set(sut.currStatements())))
                    lastAddCoverage = set(sut.currStatements())
    collectCoverage()


# print coverage
sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])
coverSum = sum(coverageCount.values())
coverMean = coverSum / (1.0*len(coverageCount))
print "MEAN COVERAGE IS",coverMean
for s in sortedCov:
    print s, coverageCount[s]
    if coverageCount[s] < coverMean:
        belowMean.add(s)
    else:
        break
print len(belowMean),"Statement below mean coverage out of", len(coverageCount)
ntests = ntests-1
# end

if (COVERAGE == 1):
    sut.internalReport()

print "TOTAL TESTS",ntests
for (t, s) in fullPool:
    print len(t), len(s)


print "TOTAL FAILED",bugs
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-start