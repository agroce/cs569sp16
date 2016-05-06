import sut
import random
import sys
import time


def randomAction():
    global actCount, bugs, coverageCount, belowMean,lastAddCoverage

    act = sut.randomEnabled(random.Random())
    actCount += 1
    ok = sut.safely(act)

    if int(sys.argv[7]):
        if len(sut.newBranches()) > 0:
            print "ACTION:",sut.randomEnabled(random.Random(int(sys.argv[2])))[0]
            for b in sut.newBranches():
                print time.time() - start, len(sut.allBranches()),"New branch",b


    if not ok:
        bugs += 1
        print "FOUND A FAILURE"
        print sut.failure()
        print "REDUCING"
        error.append(sut.test())
        for s in sut.currStatements():
            if s not in coverageCount:
                coverageCount[s] = 0
            coverageCount[s] += 1

        R = sut.reduce(sut.test(),sut.fails, True, True)
        sut.prettyPrintTest(R)
        print sut.failure()
        fail()
        sut.restart()

    else:
        if len(sut.newStatements()) != 0:
            print "NEW STATEMENTS DISCOVERED",sut.newStatements()
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

    return ok



#begin

depth = int(sys.argv[3])
width = int(sys.argv[4])
explore = 0.7
actCount = 0
sut = sut.sut()
bugs = 0
coverageCount = {}
activePool = []
fullPool = []
error=[]
noerror=[]

belowMean = set([])

print "SHOW PHASE 1"

start = time.time()
ntests = 0

while time.time()-start < int(sys.argv[1]):
    sut.restart()
    ntests += 1
    for w in xrange (0,width):
        for s in xrange(0,depth):
            if not randomAction():
                break
        for s in sut.currStatements():
            if s not in coverageCount:
                coverageCount[s] = 0
            if not (sut.newStatements() in error):
                noerror.append(sut.currStatements())
            coverageCount[s] += 1



def fail():
    print "SHOW FAILURE "
    if int(sys.argv[5]):
        print(sut.failure())
    error.append(sut.currStatements())



if int(sys.argv[6]):
    print "SHOW COVERAGE"
    sut.internalReport()



print ntests,"TESTS"


for (t,s) in fullPool:
    print len(t),len(s)


print bugs,"FAILED"
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-start

