import sut
import random
import sys
import time

BUDGET = int(sys.argv[1])
SEED = int(sys.argv[2])
depth = int(sys.argv[3])
width = int(sys.argv[3])
faults = int(sys.argv[4])
coverage_report = int(sys.argv[5])
running = int(sys.argv[6])
## parsing parameter





savedcoverage = None
Num = 0
foundbug = 0
Coverage = {}
BelowCoverage = []
i = None
weight = 0
## variable

sut = sut.sut()
rgen = random.Random()
rgen.seed(SEED)
start = time.time()
## intilize

def expandNewState():
    global sut,Coverage,sortedCov,weight,weightedCov,BelowCoverage
    for s in sut.currStatements():
        if s not in Coverage:
            Coverage[s] = 0
        Coverage[s] += 1
    sortedCov = sorted(Coverage.keys(), key=lambda x: Coverage[x])
    print "Second: coverage"
    for t in sortedCov:
        weight = (100 - Coverage[t])
        weightedCov = t*weight
        if weightedCov > 20:
            BelowCoverage.append(weightedCov)
            print "Cov:", t
            sut.backtrack(sut.state())

def main():
    global start,BUDGET,sut,savedcoverage,rgen,storedTest,act,ok,savedcoverage,running,savedcoverage,Num,faults,foundbug,savedTestState
    while time.time()-start < BUDGET:
        sut.restart()
        if (savedcoverage != None) and (rgen.random() > 0.4):
            print "Processing"
            sut.backtrack(savedcoverage)
        storedTest = False
        print "First: AVL tree"
        for s in xrange(0,100):
            act = sut.randomEnabled(rgen)
            ok = sut.safely(act)
            if len(sut.newStatements()) > 0:
                savedcoverage = sut.state()
                storedTest = True
                if(running):
                    print "New Statement",sut.newStatements()
            if (not storedTest) and (i != None) and (i in sut.currStatements()):
                savedcoverage = sut.state()
                storedTest = True
            Num += 1

            if(faults):
                if not ok:
                    foundbug += 1
                    print "Failed"
                    print sut.failure()
                    print "REDUCE"
                    R = sut.reduce(sut.test(),sut.fails, True, True)
                    sut.prettyPrintTest(R)
                    print sut.failure()
                    break
        savedTestState = sut.state()
        expandNewState()

    print foundbug,"FAILED"
    print "ACTIVE",Num
    print "RUNTIME",time.time()-start
    for s in sortedCoverage:
        print s, coverageCount[s]
    if (COVERAGE_REPORT):
        sut.internalReport()
if __name__ == '__main__':
    main()