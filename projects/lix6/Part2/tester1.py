import sut
import random
import sys
import time


TIMEOUT  = int(sys.argv[1])
SEED     = int(sys.argv[2])
DEPTH    = int(sys.argv[3])
WIDTH    = int(sys.argv[4])
FAULTS   = int(sys.argv[5])
COVERAGE = int(sys.argv[6])
RUNNING  = int(sys.argv[7])



rgen = random.Random()


LAYER_BUDGET = TIMEOUT/DEPTH

print "LAYER BUDGET:",LAYER_BUDGET

slack = 0.0

sut = sut.sut()
sut.silenceCoverage()

sut.restart()

queue = [sut.state()]
visited = []

startAll = time.time()

actCount = 0
elapsed = 0
d = 1
while d <= DEPTH:
    print "DEPTH",d,"QUEUE SIZE",len(queue),"VISITED SET",len(visited)
    d += 1
    frontier = []
    startLayer = time.time()
    scount = 0
    for s in queue:
        scount += 1
        sut.backtrack(s)
        allEnabled = sut.enabled()
        rgen.shuffle(allEnabled)
        for a in allEnabled:
            elapsed = time.time() - startLayer
            if elapsed >= LAYER_BUDGET:
                break
            ok = sut.safely(a)
            actCount += 1
            if not ok:
                print "FOUND A FAILURE"
                #sut.prettyPrintTest(sut.test())
                print sut.failure()
                print "REDUCING"
                R = sut.reduce(sut.test(),sut.fails, True, True)
                sut.prettyPrintTest(R)
                print sut.failure()
                #sys.exit(1)
            s2 = sut.state()
            if s2 not in visited:
                visited.append(s2)
                frontier.append(s2)
            sut.backtrack(s)
        if elapsed >= LAYER_BUDGET:
            print "DID NOT GET TO EXPAND",len(queue)-scount,"STATES"
            break
    elapsed = time.time() - startLayer
    slack = float(LAYER_BUDGET-elapsed)
    print "SLACK",slack
    if (d < DEPTH) and (slack > 0):
        LAYER_BUDGET = LAYER_BUDGET+slack/(DEPTH-d)
        print "NEW LAYER BUDGET",LAYER_BUDGET
    queue = frontier
sut.internalReport()

print "SLACK",slack
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-startAll
