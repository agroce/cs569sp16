import sut
import random
import sys

rgen = random.Random()

DEPTH = 100
#NUM_TESTS = 100

sut = sut.sut()
sut.silenceCoverage()

sut.restart()

queue = [sut.state()]
visited = []

d = 1
while d <= DEPTH:
    print "DEPTH",d,"QUEUE SIZE",len(queue)
    d += 1
    frontier = []
    for s in queue:
        sut.backtrack(s)
        for a in sut.enabled():
            sut.safely(a)
            s2 = sut.state()
            if s2 not in visited:
                visited.append(s2)
                frontier.append(s2)
    queue = frontier
    sut.internalReport()


