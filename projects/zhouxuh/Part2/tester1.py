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

def action():
    global actCount, bugs, failPool
    act = sut.randomEnabled(rgen)
    actCount += 1
    ok = sut.safely(act)
    if running == 1:
            if len(sut.newBranches()) > 0:
                print "ACTION:", act[0]
                for b in sut.newBranches():
                    print time.time() - start, len(sut.allBranches()), "New branch", b
    if faults:
        if not ok:
            bugs += 1
            print "FOUND A FAILURE"
            print sut.failure()
            print "REDUCING"
            failPool.append(sut.test())
            collectCoverage()
            R = sut.reduce(sut.test(),sut.fails, True, True)
            sut.prettyPrintTest(R)
            print sut.failure()
            
            f = open(("failure" + str(bugs) + ".test"),"w")
            f.writelines(str(sut.failure()))
            f.close()
            
            sut.restart()
        else:
            expand()
    
    return ok

def expand():
    global lastAddCoverage
    if len(sut.newStatements()) != 0:
        print "NEW STATEMENTS DISCOVERED",sut.newStatements()
        oldTest = list(sut.test())
        storeTest = sut.reduce(oldTest,sut.coversStatements(sut.newStatements()))
        print "OLD LENGTH = ",len(oldTest),"NEW LENGTH = ",len(storeTest)
        sut.replay(oldTest)
        fullPool.append((storeTest, set(sut.currStatements())))
        lastAddCoverage = set(sut.currStatements())
        return


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
failPool = []
fullPool = []
ntests = 0

start = time.time()
while time.time()-start < timeout:
    sut.restart()
    ntests += 1
    for s in xrange(0,depth):
        if not action():
            break
    collectCoverage()    


if (coverage == 1):
    sut.internalReport()

print ntests,"TESTS"

print bugs,"FAILED"
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-start