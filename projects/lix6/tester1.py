import sut
import random
import sys
import time
import math



#Functions

def collectCoverage():
    global coveraged
    for s in sut.currStatements():
        if s not in coveraged:
            coveraged[s] = 0
        coveraged[s] += 1

def randomAction():
    global actCount, bugs, visited
    act = sut.randomEnabled(rgen)
    actCount += 1
    ok = sut.safely(act)
    if not ok:
        bugs += 1
        if FAULTS:
            file = "failure"+str(bugs)+".test"
            f = open(file,'a')
            f.write(str(sut.failure()))
            f.close()
            if COVERAGE:
                collectCoverage()
            sut.restart()
    else:
        if RUNNING:
            if sut.newBranches() != set([]):
                for b in sut.newBranches():
                    print  time.time() - start, len(sut.allBranches()) ,"new branch", b
        if len(sut.newStatements()) != 0:
            visited.append((list(sut.test()), set(sut.currStatements())))
    return ok




start = time.time()


TIMEOUT    = int(sys.argv[1])    #
SEED       = int(sys.argv[2])    #
DEPTH      = int(sys.argv[3])    #
WIDTH      = int(sys.argv[4])
FAULTS     = int(sys.argv[5])    #
COVERAGE   = int(sys.argv[6])    #
RUNNING    = int(sys.argv[7])

#global variables are defined here
sut        = sut.sut()
sut.silenceCoverage()
rgen       = random.Random()
rgen.seed(SEED)
actCount   = 0
bugs       = 0
coveraged  = {}
visited    = []





print "STARTING PHASE 1"

while time.time() - start < TIMEOUT * 0.5:
    sut.restart()

    for s in xrange(0,DEPTH):
        randomAction()
    collectCoverage()

sortedCov = sorted(coveraged.keys(), key=lambda x: coveraged[x])
for s in sortedCov:
    print s, coveraged[s]



print "STARTING PHASE 2"

while time.time() - start < TIMEOUT :
    belowMedian = set([])
    sort = sorted(coveraged.keys(),key = lambda x : coveraged[x])

    a = len(sort)/2


    for s in sort:
        if coveraged[s] < sort[a]:
            belowMedian.add(s)
        else:
            break
       	
    
    activePool = []
    for (t,c) in visited:
        for s in c:
            if s in belowMedian:
                activePool.append((t,c))
                break
    sut.restart()
    if len(sut.newStatements()) != 0:
        print "new statement",sut.newStatements()
        visited.append((list(sut.test()), set(sut.currStatements())))
    for s in xrange(0,DEPTH):
        if not randomAction():
            break
    collectCoverage()

sortedCov = sorted(coveraged.keys(), key=lambda x: coveraged[x])
for s in sortedCov:
    print s, coveraged[s]




if COVERAGE:
    sut.internalReport()

print "FAILURES ",bugs, "TIMES"
print "TOTAL ACTIONS", actCount
print "TOTAL RUNTIME", time.time()-start





        

