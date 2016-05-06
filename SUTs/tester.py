import sut
import random
import sys
import time

depth = 100

explore = 0.7

savedTest = None

actCount = 0

sut = sut.sut()

BUDGET = int(sys.argv[1])
SEED = int(sys.argv[2])
depth = int(sys.argv[3])
width = int(sys.argv[3])
faults = int(sys.argv[4])
coverage_report = int(sys.argv[5])
running = int(sys.argv[6])

bugs = 0

rgen = random.Random()
rgen.seed(SEED)


coverageCount = {}
coverageWeightedBelowMean = []
leastCovered = None
weight = 0

userDefCov = 100
# coverage tolerance
covTolerance = 400


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
            if(running):
                print "FOUND NEW STATEMENTS",sut.newStatements()
        if (not storedTest) and (leastCovered != None) and (leastCovered in sut.currStatements()):
            #print "SAW LEAST COVERED STATEMENT, STORING TEST"
            savedTest = sut.state()
            storedTest = True
        actCount += 1

        if(faults):
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

    savedTestState = sut.state()
    for s in sut.currStatements():
        if s not in coverageCount:
            coverageCount[s] = 0
        coverageCount[s] += 1
    sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])
    # go through the sortedCov and assign weights on them
    print "Step two: Weight the coverage"
    # weight is calculated by: coverage * (userDefCov - coverageCount),
    # the greater the difference between the userDefCov and the coverage count,
    # the larger your weight will be
    for t in sortedCov:
        weight = (userDefCov - coverageCount[t])
        weightedCov = t*weight
        if weightedCov > covTolerance:
            coverageWeightedBelowMean.append(weightedCov)
            print "statement below coverage:", t
            print "Backtracking...."
            # back track the statement below certain coverage
            sut.backtrack(sut.state())

if(coverage_report):
    sut.internalReport()
    sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])
    for s in sortedCov:
        print s, coverageCount[s]

print bugs,"FAILED"
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-start
