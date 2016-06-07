import sut
import random
import sys
import time
import math

depth = 100

explore = 0.7

savedTest = None

actCount = 0

sut = sut.sut()

BUDGET = int(sys.argv[1])
SEED = int(sys.argv[2])
depth = int(sys.argv[3])
width = int(sys.argv[4])
faults = int(sys.argv[5])
coverage_report = int(sys.argv[6])
running = int(sys.argv[7])
instruction = int(sys.argv[8])

if(instruction == 1):
    print "First parameter: Time BUDGET, Second: SEED, Third: Test Depth, Fourth: Width, Fifth: Faults, Sixth: Print coverage report? Seventh: running coverage?"
    print "All of the parameters take in either 0 or 1"
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
        elapsed = time.time() - start

        if(running == 1):
            if len(sut.newBranches()) > 0:
                print "Action", act[0]
                for b in sut.newBranches():
                    print elapsed, len(sut.allBranches()), "New branch", b

        if len(sut.newStatements()) > 0:
            savedTest = sut.state()
            storedTest = True
            if(running == 1):
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
            #sut.prettyPrintTest(R)
            print sut.failure()
            if(faults == 1):
                filename = "failure" +  str(bugs) + ".test"
                sut.saveTest(sut.test(), filename)
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
        # try using statistical distance in my algorithm
        weight = math.sqrt((math.pow(userDefCov,2)) + math.pow(coverageCount[t], 2))
        # min statistical error
        weight_min_error = float(1/math.sqrt(weight))
        weightedCov = coverageCount[t]*weight*weight_min_error

        if weightedCov > covTolerance:
            coverageWeightedBelowMean.append(weightedCov)
            print "statement below coverage:", t
            print "Backtracking...."
            # back track the statement below certain coverage
            sut.backtrack(sut.state())

sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])
for s in sortedCov:
    print s, coverageCount[s]
if(coverage_report == 1):
    sut.internalReport()

print bugs,"FAILED"
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-start
