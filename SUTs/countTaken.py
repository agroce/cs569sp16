import sut
import random
import sys
import time
from functools import partial

def abstract(name):
    abs = ""
    for c in name:
        if c not in ['0','1','2','3','4','5','6','7','8','9']:
            abs += c
    return abs        

rgen = random.Random()
depth = 100

actCount = 0

BUDGET = 60.0

sut = sut.sut()
k = int(sys.argv[1])

actionCount = {}
for action in sut.actions():
    actionCount[abstract(action[0])] = 0

bugs = 0

start = time.time()
while time.time()-start < BUDGET:
    sut.restart()
    for s in xrange(0,depth):
        acts = sut.randomEnableds(rgen,k)
        sortActs = sorted(acts, key=lambda x:actionCount[abstract(x[0])])
        act = sortActs[0]
        ok = sut.safely(act)
        actCount += 1
        actionCount[abstract(act[0])] += 1
        if not ok:
            bugs += 1
            print "FOUND A FAILURE"
            #sut.prettyPrintTest(sut.test())
            print sut.failure()
            print "REDUCING"
            R = sut.reduce(sut.test(),sut.fails, True, True)
            sut.prettyPrintTest(R)
            print sut.failure()
            sut.restart()                    

sut.internalReport()

orderedActs = sorted(actionCount.keys(), key = lambda x: actionCount[x])
for act in orderedActs:
    print act, actionCount[act]

print bugs,"FAILED"
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-start
