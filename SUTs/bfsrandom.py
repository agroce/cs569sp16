import sut
import random
import sys
import time

rgen = random.Random()

#NUM_TESTS = 100

GOAL_DEPTH = 11
BUDGET = 60.0

LAYER_BUDGET = BUDGET/GOAL_DEPTH
slack = 0.0

sut = sut.sut()
sut.silenceCoverage()

sut.restart()

queue = [sut.state()]
visited = []

elapsed = 0
d = 1
while d <= GOAL_DEPTH:
    print "DEPTH",d,"QUEUE SIZE",len(queue),"VISITED SET",len(visited)
    d += 1
    frontier = []
    startLayer = time.time()
    for s in queue:
        sut.backtrack(s)
        allEnabled = sut.enabled()
        rgen.shuffle(allEnabled)
        for a in allEnabled:
            elapsed = time.time() - startLayer
            if elapsed >= LAYER_BUDGET:
                break
            sut.safely(a)
            s2 = sut.state()
            if s2 not in visited:
                visited.append(s2)
                frontier.append(s2)
        if elapsed >= LAYER_BUDGET:
            break
    elapsed = time.time() - startLayer
    slack += LAYER_BUDGET-slack
    queue = frontier
    sut.internalReport()

print slack

