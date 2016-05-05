import sut
import random
import sys
import time

rgen = random.Random()
depth = 100

explore = 0.7

savedTest = None

actCount = 0

sut = sut.sut()

BUDGET = int(sys.argv[1])
seed = int(sys.argv[2])
width = int(sys.argv[3])
faults = int(sys.argv[4])
coverage = int(sys.argv[5])
running = int(sys.argv[6])

bugs = 0

coverageCount = {}
coverageWeightedBelowMean = []
leastCovered = None
weight = 0
totalCov = 100
# coverage tolerance
covTolerance = 25


start = time.time()

while time.time()-start < BUDGET:
    sut.restart()
    if (savedTest != None) and (rgen.random() > explore):
        print "EXPLOITING"
        sut.backtrack(savedTest)
    storedTest = False

    print "Step one: test AVL tree"
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
    # go through the sortedCov and assign weights on them
    print "Step two: Weight the coverage"
    # weight is calculated by: coverage * (mean - coverageCount),
    # the greater the difference between the mean and the coverage count,
    # the larger your weight will be
    for t in sortedCov:
        weight = (totalCov - coverageCount[t])
        weightedCov = t*weight
        if weightedCov > covTolerance:
            coverageWeightedBelowMean.append(weightedCov)
            print "statement below coverage:", t

sut.internalReport()
sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])

for s in sortedCov:
    print s, coverageCount[s]

print bugs,"FAILED"
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-start
