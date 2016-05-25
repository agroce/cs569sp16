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
width = int(sys.argv[4])
faults = int(sys.argv[5])
coverage_report = int(sys.argv[6])
running = int(sys.argv[7])


collectedstatementNum = 400
bugs = 0

rgen = random.Random()
rgen.seed(SEED)
CovW = []
coverageCount = {}
CovWeight = []
startT = time.time()
mincover = None


      


while time.time()-startT < BUDGET:
    sut.restart()
    if (savedTest != None) and (rgen.random() > explore):
        print "EXPLOITING"
        sut.backtrack(savedTest)
    storedTest = False

    for s in xrange(0,depth):
        act = sut.randomEnabled(rgen)
        ok = sut.safely(act)
        actCount += 1
        if (running == 1):
            if len(sut.newBranches()) > 0:
                print "ACTION:", act[0]
                for b in sut.newBranches():
                    print time.time() - startT, len(sut.allBranches()), "New branch", b

        if(faults):
            if not ok:
                bugs += 1
                print "FOUND A FAILURE"
              
                print sut.failure()
                print "REDUCING"
                R = sut.reduce(sut.test(),sut.fails, True, True)
                sut.prettyPrintTest(R)
                print sut.failure()
				fname = 'failure'+str(bugs)+'.test'
				sut.saveTest(R,fname)
                break
            else:
               if len(sut.newStatements()) > 0:
                savedTest  = sut.state()
                storedTest = True
                print "FOUND NEW STATEMENTS", sut.newStatements()


    for s in sut.currStatements():
        if s not in coverageCount:
            coverageCount[s] = 0
        coverageCount[s] += 1
    sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])

    for t in sortedCov:
        print t, coverageCount[t]

if(coverage_report):
    sut.internalReport()
    sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])
    for s in sortedCov:
        print s, coverageCount[s]

print bugs,"FAILED"
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-startT