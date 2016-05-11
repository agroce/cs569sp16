import sut
import random
import time
import sys

def mutate(test):
    tcopy = list(test)
    i = r.randint(0,len(tcopy))
    sut.replay(tcopy[:i])
    e = sut.randomEnabled(r)
    sut.safely(e)
    trest = [e]
    for s in tcopy[i+1:]:
        if s[1]():
            trest.append(s)
            sut.safely(s)
    tcopy = test[:i]+trest
    return tcopy
    
BUDGET = int(sys.argv[1])
SEED = int(sys.argv[2])
start = time.time()

sut = sut.sut()

r = random.Random()
r.seed(SEED)

INITIAL_POP = 10 
LENGTH = 10

BEST = 5

population = []

for i in xrange(0,INITIAL_POP):
    sut.restart()
    for s in xrange(0,LENGTH):
        sut.safely(sut.randomEnabled(r))
    population.append((list(sut.test()),set(sut.currBranches())))

print "STARTING POP BRANCHCOV",len(sut.allBranches())
print "STARTING POP STATEMENTCOV",len(sut.allStatements())

while (time.time()-start) < BUDGET:
    sortPop = sorted(population,key = lambda x: len(x[1]),reverse=("bad" in sys.argv))
    (t,b) = r.choice(sortPop[:BEST])
    m = mutate(t)
    population.append((m,sut.currBranches()))

#sut.internalReport()
print "FINAL POP BRANCHCOV",len(sut.allBranches())
print "FINAL POP STATEMENTCOV",len(sut.allStatements())    
