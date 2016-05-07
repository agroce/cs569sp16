import sut
import random
import sys
import time

#begin
timeout = int(sys.argv[1])
seed = int(sys.argv[2])
depth = int(sys.argv[3])
width = int(sys.argv[4])
faults = int(sys.argv[5])
coverage = int(sys.argv[6])
running = int(sys.argv[7])

actCount = 0
sut = sut.sut()
bugs = 0
coverageCount = {}
fullPool = []
error=[]
noerror=[]
belowMean = set([])
start = time.time()
ntests = 0

print "STARTING PHASE 1"
def randomAction():
    global actCount, bugs, coverageCount, belowMean,lastAddCoverage

    act = sut.randomEnabled(random.Random())
    actCount += 1
    ok = sut.safely(act)

    if running:
        if len(sut.newBranches()) > 0:
            print "ACTION:",sut.randomEnabled(random.Random(seed))[0]
            for b in sut.newBranches():
                print time.time() - start, len(sut.allBranches()),"New branch",b
            for s1 in sut.newStatements():
                print time.time() - start, len(sut.allStatements()),"New statement",b

    if not ok or not sut.check():
        bugs += 1
        print "FOUND A FAILURE"
        if faults:
            print("SHOW FAULT")
            print sut.failure()
            error.append(sut.test())
            R = sut.reduce(sut.test(),sut.fails, True, True)
            sut.prettyPrintTest(R)
            print sut.failure()
            sut.restart()

    return ok

while time.time()-start < timeout:
    sut.restart()
    ntests += 1
    for s in xrange(0,depth):
        if not randomAction():
           break
    for s in sut.currStatements():
        if s not in coverageCount:
            coverageCount[s] = 0
        if not (sut.newStatements() in error):
            noerror.append(sut.currStatements())
        coverageCount[s] += 1

print "STARTING PHASE 2"
start = time.time()

def belowMeans():
    sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])
    coverSum = sum(coverageCount.values())
    coverMean = coverSum / (1.0*len(coverageCount))
    for s in sortedCov:
        if coverageCount[s] < coverMean:
            belowMean.add(s)
        else:
            break
while time.time()-start < seed:
    ntests += 1
    belowMeans()
    for s in xrange(0,depth):
        if not randomAction():
            break
    if time.time()-start > timeout:
        break

if coverage:
    print "SHOW COVERAGE"
    sut.internalReport()

print ntests,"TESTS"

print bugs,"FAILED"
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-start

