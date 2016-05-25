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
                for s in sut.newStatements():
                    print time.time() - start, len(sut.allStatements()),"New statement",s
    
    if not ok:
        if faults:
            bugs += 1
            print "FOUND A FAILURE"
            print sut.failure()
            print "REDUCING"
            failPool.append(sut.test())
            collectCoverage()
            R = sut.reduce(sut.test(),sut.fails, True, True)
            sut.prettyPrintTest(R)
            print sut.failure()
            fname="failure" + str(bugs) + ".test"
            sut.saveTest(sut.test(),fname)
            errorSeqs.append(sut.currStatements())
            sut.restart()
    else: 
        expand()

    return ok

def expand():
    global lastAddCoverage
    nonErrorSeqs.append(sut.currStatements())
    if len(sut.newStatements()) != 0:
        print "NEW STATEMENTS DISCOVERED",sut.newStatements()
        newSeq = sut.newStatements()
        if (newSeq in nonErrorSeqs or newSeq in errorSeqs):
           action()
           #sut.restart() 
        else:
            oldTest = list(sut.test())
            storeTest = sut.reduce(oldTest,sut.coversStatements(newSeq))
            print "OLD LENGTH = ",len(oldTest),"NEW LENGTH = ",len(storeTest)
            sut.replay(oldTest)
            fullPool.append((storeTest, set(sut.currStatements())))
            lastAddCoverage = set(sut.currStatements())
        return

def belowmean():
    global belowMean
    sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])
    coverSum = sum(coverageCount.values())
    coverMean = coverSum / (1.0*len(coverageCount))
    for s in sortedCov:
        if coverageCount[s] < coverMean:
            belowMean.add(s)
        else:
            break

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
errorSeqs= []
nonErrorSeqs = []
newSeq   = None
queue = [sut.state()]
visited = []
belowMean = set([])
ntests = 0


start = time.time()

print "PHASE 1"
while time.time()-start < timeout*0.7:
    sut.restart()
    ntests += 1
    for s in xrange(0,depth):
        if not action():
            break

    collectCoverage()

print "PHASE 2"
while time.time()-start < timeout:
    belowmean()
    sut.restart()
    ntests += 1
    for s in xrange(0,depth):
        if not action():
            break

    collectCoverage()

if coverage:
    sut.internalReport()

print ntests,"TESTS"

print bugs,"FAILED"
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-start
