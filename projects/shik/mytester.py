import sut
import random
import sys
import time
import math


TIMEOUT = int(sys.argv[1])

SEED = int(sys.argv[2])

DEPTH = int(sys.argv[3])

WIDTH = int(sys.argv[4])

FAULTS = int(sys.argv[5])

COVERAGE = int(sys.argv[6])

RUNNING = int(sys.argv[7])

RESULT = int(sys.argv[8])




def randomAction():
    global actCount, bugs, visited
    act = sut.randomEnabled(rgen)
    actCount += 1
    ok = sut.safely(act)
    elapsed = time.time() - start
    if not ok:
        bugs += 1
        if FAULTS:
            name = "failure"+str(bugs)+".test"
            f = sut.test()
            sut.saveTest(f,name)
    else:
        if RUNNING:
            if sut.newBranches() != set([]):
                print "ACTION:",act[0]
                for d in sut.newBranches():
                    print elapsed,len(sut.allBranches()),"New branch",d
                sawNew = True
            else:
                sawNew = False

            if sut.newStatements() != set([]):
                print "ACTION:",act[0]
                for s in sut.newStatements():
                    print elapsed,len(sut.allStatements()),"New statement",s
                sawNew = True
            else:
                sawNew = False

        if len(sut.newStatements()) != 0:
            visited.append((list(sut.test()), set(sut.currStatements())))
    
    return ok



def collectCoverage():
    global coverageCount
    for s in sut.currStatements():
        if s not in coverageCount:
            coverageCount[s] = 0
        coverageCount[s] += 1

def findMid():
    global belowMid
    sortedCov = sorted(coverageCount.keys(),key = lambda x : coverageCount[x])
    ss = len(sortedCov)/2
    for s in sortedCov:
        if coverageCount[s] < sortedCov[ss]:
            belowMid.add(s)
        else:
            break


start = time.time()

sut = sut.sut()
sut.silenceCoverage()

rgen = random.Random()
rgen.seed(SEED)

actCount  = 0
bugs = 0

coverageCount  = {}
visited = []

print "STARTING FIRST HALF TIME"

while time.time() - start < TIMEOUT/2.:
    sut.restart()
    for s in xrange(0,DEPTH):
        if not randomAction():
            break
    collectCoverage()

sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])  

ss = len(coverageCount)/2
coverMid = sortedCov[ss]
print "MID COVERAGE IS",coverMid

for s in sortedCov:
    print s, coverageCount[s]


print "STARTING REST HALF TIME"

while time.time() - start < TIMEOUT :
    belowMid = set([])
    
    findMid()   	
    activePool = []

    for (t,c) in visited:
        for s in c:
            if s in belowMid:
                activePool.append((t,c))
                break

    sut.restart()

    for s in xrange(0,DEPTH):
        if not randomAction():
            break
    collectCoverage()



print "\nBelowMid coverageCount 2nd running Coverage results: "

sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])
ss = len(coverageCount)/2
coverMid = sortedCov[ss]
for s in sortedCov:
    print s, coverageCount[s]

print "\nBelowMid coverageCount 2nd running Coverage results has printed\n"


if COVERAGE:
    sut.internalReport()

if RESULT:
    print bugs,"FAILED"
    print "TOTAL ACTIONS", actCount
    print "TOTAL RUNTIME", time.time()-start



