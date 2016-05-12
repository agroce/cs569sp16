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

print 'USAGE: <budget> <seed> <length> <initial_pop> <best#> <mode = best/worst/random>'
    
BUDGET = int(sys.argv[1])
SEED = int(sys.argv[2])
LENGTH = int(sys.argv[3])
INITIAL_POP = int(sys.argv[4])
BEST = int(sys.argv[5])
MODE = sys.argv[6] # either "best" "worst" or "random"
start = time.time()

sut = sut.sut()

r = random.Random()
r.seed(SEED)

population = []

for i in xrange(0,INITIAL_POP):
    sut.restart()
    for s in xrange(0,LENGTH):
        sut.safely(sut.randomEnabled(r))
    population.append((list(sut.test()),set(sut.currBranches())))

print "STARTING POP BRANCHCOV",len(sut.allBranches())
print "STARTING POP STATEMENTCOV",len(sut.allStatements())

while (time.time()-start) < BUDGET:
    if MODE != "random":
        sortPop = sorted(population,key = lambda x: len(x[1]),reverse=(MODE=="best"))
        (t,b) = r.choice(sortPop[:BEST])
    else:
        (t,b) = r.choice(population)
    m = mutate(t)
    population.append((m,sut.currBranches()))

#sut.internalReport()
print "FINAL POP BRANCHCOV",len(sut.allBranches())
print "FINAL POP STATEMENTCOV",len(sut.allStatements())    
