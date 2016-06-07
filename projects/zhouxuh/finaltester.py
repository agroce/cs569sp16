import sut
import random
import sys
import time

def run(act):
    if running:
        if len(sut.newBranches()) > 0:
            print "ACTION:", act[0]
            for b in sut.newBranches():
                print time.time() - start, len(sut.allBranches()), "New branch", b
    
def action():
    global actCount, bugs
    act = sut.randomEnabled(rgen)
    actCount += 1
    newSeq.append(act)
    for s in xrange(0,depth/2):
        if time.time() > start + timeout:
            break
        if (newSeq not in nonErrorSeqs) and (newSeq not in errorSeqs):
            break
        else:
            newSeq.pop()
            act = sut.randomEnabled(rgen)
            newSeq.append(act)
    
    ok = sut.safely(act)
    run(act)

    if ok:
        nonErrorSeqs.append(newSeq)
    if not ok:
        if time.time() > start + timeout:
            return not ok
        if faults:
            bugs += 1
            print "FOUND A FAILURE"
            print sut.failure()  
            fname="failure" + str(bugs) + ".test"
            sut.saveTest(sut.test(),fname)
            errorSeqs.append(newSeq)
            sut.restart()
    return ok

timeout  = int(sys.argv[1])
seed     = int(sys.argv[2])
depth    = int(sys.argv[3])
width    = int(sys.argv[4])
faults   = int(sys.argv[5])
coverage = int(sys.argv[6])
running  = int(sys.argv[7])

rgen = random.Random()
rgen.seed(seed)
sut = sut.sut()
actCount = 0
bugs = 0
ntests = 0
errorSeqs= []
nonErrorSeqs = []
newSeq = []
start = time.time()

while time.time() < start + timeout:
    sut.restart()
    ntests += 1
    for s in xrange(0,depth):
        if time.time() > start + timeout:
            break
        if not action():
            break

if coverage:
    sut.internalReport()

print ntests,"TESTS"
print bugs,"FAILED"
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-start
