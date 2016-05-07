import sut
import random
import sys
import time

timeout  = int(sys.argv[1])
seed     = int(sys.argv[2])
depth    = int(sys.argv[3])
width    = int(sys.argv[4])
faults   = int(sys.argv[5])
coverage = int(sys.argv[6])
running  = int(sys.argv[7])

rgen = random.Random()
rgen.seed(seed)
actCount = 0
sut = sut.sut()
bugs = 0
coverageCount = {}
fullPool = []
failPool = []
belowMean = set([])
start = time.time()
ntests = 0


while time.time() - start < timeout:
    sut.restart()
    ntests += 1
    for s in xrange(0, depth):
        act = sut.randomEnabled(rgen)
        actCount += 1
        ok = sut.safely(act)
        if running == 1:
            if len(sut.newBranches()) > 0:
                print "ACTION:", act[0]
                for b in sut.newBranches():
                    print time.time() - start, len(sut.allBranches()), "NEW BRANCH", b
        if not ok:
            bugs += 1
            print "FOUND A FAILURE"
            print sut.failure()
            print "REDUCING"
            failPool.append(sut.test())
            for s in sut.currStatements():
                if s not in coverageCount:
                    coverageCount[s] = 0
                coverageCount[s] += 1

            R = sut.reduce(sut.test(),sut.fails, True, True)
            sut.prettyPrintTest(R)
            print sut.failure()
            sut.restart()
            break
        else:
            if len(sut.newStatements()) != 0:
                print "NEW STATEMENTS DISCOVERED",sut.newStatements()
                oldTest = list(sut.test())
                storeTest = sut.reduce(oldTest,sut.coversStatements(sut.newStatements()))
                print "OLD LENGTH = ",len(oldTest),"NEW LENGTH = ",len(storeTest)
                sut.replay(oldTest)
                fullPool.append((storeTest, set(sut.currStatements())))
                lastAddCoverage = set(sut.currStatements())


            for s in belowMean:
                if s in sut.currStatements() and s not in lastAddCoverage:
                    print "NEW PATH TO LOW COVERAGE STATEMENT",s
                    fullPool.append((list(sut.test()), set(sut.currStatements())))
                    lastAddCoverage = set(sut.currStatements())

    for s in sut.currStatements():
        if s not in coverageCount:
            coverageCount[s] = 0
        coverageCount[s] += 1


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
print len(belowMean),"STATEMENTS BELOW MEAN COVERAGE OUT OF", len(coverageCount)


if (coverage == 1):
    sut.internalReport()

print ntests,"TESTS"
for (t, s) in fullPool:
    print len(t), len(s)


print bugs,"FAILED"
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-start