import sut
import random
import sys
import time

rgen = random.Random()
depth = 100

explore = 0.7

savedTest = None

actCount = 0
BUDGET = int(sys.argv[1])

sut = sut.sut()

bugs = 0

coverageCount = {}
leastCovered = None

start = time.time()
while time.time()-start < BUDGET:
    sut.restart()
    if (savedTest != None) and (rgen.random() > explore):
        print "EXPLOITING"
        sut.backtrack(savedTest)
    storedTest = False    
    for s in xrange(0,depth):
        act = sut.randomEnabled(rgen)

        ok = sut.safely(act)   
        if len(sut.newStatements()) > 0:
            savedTest = sut.state()
            storedTest = True
            print "FOUND NEW STATEMENTS",sut.newStatements()
        if (not storedTest) and (leastCovered != None) and (leastCovered in sut.currStatements()):
            #print "SAW LEAST COVERED STATEMENT, STORING TEST"
            savedTest = sut.state()
            storedTest = True
        actCount += 1
        if not ok:
            bugs += 1
            print "FOUND A FAILURE"
            #sut.prettyPrintTest(sut.test())
            print sut.failure()
            print "REDUCING"
            R = sut.reduce(sut.test(),sut.fails, True, True)
            sut.prettyPrintTest(R)
            print sut.failure()
            break
    for s in sut.currStatements():
        if s not in coverageCount:
            coverageCount[s] = 0
        coverageCount[s] += 1    
    sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])
    leastCovered = sortedCov[0]
    print "LEAST COVERED STATEMENT IS",leastCovered,coverageCount[leastCovered]

sut.internalReport()

sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])

for s in sortedCov:
    print s, coverageCount[s] 

print bugs,"FAILED"
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-start
