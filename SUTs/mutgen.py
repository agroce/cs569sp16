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
    if len(sut.newCurrBranches()) != 0:
        print "NEW BRANCHES DUE TO MUTATION:",sut.newCurrBranches()
    return tcopy

def crossover(test,test2):
    tcopy = list(test)
    i = r.randint(0,len(tcopy))
    sut.replay(tcopy[:i])
    trest = []
    for s in test2[i:]:
        if s[1]():
            trest.append(s)
            sut.safely(s)
    tcopy = test[:i]+trest
    if len(sut.newCurrBranches()) != 0:
        print "NEW BRANCHES DUE TO CROSSOVER:",sut.newCurrBranches()
    return tcopy

print 'USAGE: <budget> <seed> <length> <initial_pop> <best#> <mode = best/worst/random>'
    
BUDGET = int(sys.argv[1])
SEED = int(sys.argv[2])
LENGTH = int(sys.argv[3])
INITIAL_POP = int(sys.argv[4])
BEST = int(sys.argv[5])
MODE = sys.argv[6] # either "best" "worst" or "random"
PCROSSOVER = float(sys.argv[7])
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
    if r.random() > PCROSSOVER:    
        m = mutate(t)
    else:
        (t2,b) = r.choice(sortPop[:BEST])
        m = crossover(t,t2)
    population.append((m,sut.currBranches()))

#sut.internalReport()
print "FINAL POP BRANCHCOV",len(sut.allBranches())
print "FINAL POP STATEMENTCOV",len(sut.allStatements())    
