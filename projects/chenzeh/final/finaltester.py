
## This version is my last result demons, This version 
## based on last two projects and add mutation function
## and crosscover

## Zehuan Chen

import sut
import random
import sys
import time
import traceback

timeout = int(sys.argv[1])
SEED = int(sys.argv[2])
DEPTH = int(sys.argv[3])
WIDTH = int(sys.argv[4])
FAULT_CHECK = int(sys.argv[5])
COVERAGE_REPORT = int(sys.argv[6])
RUN= int(sys.argv[7])


MAX_DEPTH = DEPTH
elapsed = 0
bestNum = 20
errors = []
corrects = []
population = []


def makerun():
    if  RUN:
        
        if sut.newBranches() != set([]):
            
            print "ACTION:",action[0]
            for b in sut.newBranches():
                print elapsed,len(sut.allBranches()),"New branch",b
            findNew = True
        else:
            findNew = False
            
        if sut.newStatements() != set([]):
            
            print "ACTION:",action[0]
            for s in sut.newStatements():
                print elapsed,len(sut.allStatements()),"New statement",s
            findNew = True
        else:
            findNew = False


def fault_collection(bugs):
    
    if(FAULT_CHECK):
        print "use"+str(time.time()-startAll)
        print "FOUND A FAILURE"
        print sut.failure()
        print "REDUCING"
        
        R = sut.reduce(sut.test(),sut.fails, True, True)
        sut.prettyPrintTest(R)
        
        print "this is fault:"+ str(sut.failure())
        fname = 'failure'+str(bugs)+'.test'
        sut.saveTest(R,fname)
        

def mutate(test,bugs):

    tcopy = list(test)
    erro = sut.randomEnabled(rgen)
    isok = sut.safely(erro)
    i = rgen.randint(0,len(tcopy))
    sut.replay(tcopy[:i])
    
    
    if not isok:
       bugs += 1
       errors.append(sut.currStatements())
       fault_collection()

    trest = [erro]

    for s in tcopy[i+1:]:
        if s[1]():
            trest.append(s)
            sut.safely(s)
    tcopy = test[:i]+trest
    

    if len(sut.newCurrBranches()) != 0:
        print "MUTATION NEW BRANCH FOUND:",sut.newCurrBranches()
    return tcopy


def crossover(test,test2,bugs):
    
    tcopy = list(test)
    i = rgen.randint(0,len(tcopy))
    sut.replay(tcopy[:i])
    
    trest = []

    for s in test2[i:]:
        if s[1]():
            
            trest.append(s)
            isok = sut.safely(s)
            
            if not isok:
                bugs += 1
                errors.append(sut.currStatements())
                fault_collection()

    tcopy = test[:i]+trest

    if len(sut.newCurrBranches()) != 0:
        print "NEW BRANCHES DUE TO CROSSOVER:",sut.newCurrBranches()
    return tcopy

rgen = random.Random()
rgen.seed(SEED+1)
sut = sut.sut()
sut.silenceCoverage()
sut.restart()
states = [sut.state()]
startAll = time.time()

bugs = 0

while time.time()-startAll<timeout/2.:
    for s in states:
        elapsedTime = time.time()-startAll
        
        if elapsedTime>=timeout:
            break
        
        sut.restart()
        sut.backtrack(s)

        for w in xrange(0,WIDTH):
            for d in xrange(0,MAX_DEPTH):
                
                if (time.time()-startAll)>timeout:
                    break
                
                action = sut.randomEnabled(rgen)
                isok = sut.safely(action)
                elapsed = time.time() - startAll
                makerun()
                news = sut.newStatements()

                if not isok:
                    bugs += 1
                    errors.append(sut.currStatements())
                    fault_collection(bugs)
                    
                if((len(news)>0)and not(news in errors) and not( news in corrects)):
                    states.append(sut.state())
                    corrects.append(sut.currStatements())


        population.append((list(sut.test()),set(sut.currBranches())))


while time.time()-startAll<timeout*0.75:

    sortPop = sorted(population,key = lambda x: len(x[1]),reverse=True)
    (test1,b) = rgen.choice(sortPop[:bestNum])
    (test2,b) = rgen.choice(sortPop[:bestNum])
    m = mutate(test1,bugs)
    c = crossover(test1,test2,bugs)
    population.append((m,sut.currBranches()))
    population.append((c,sut.currBranches()))
    if elapsed >= timeout *0.75:
            print "Stopping Test ", len(sut.test())
            print time.time()-startAll, "RUNTIME"
            break


if (COVERAGE_REPORT):
    sut.internalReport()
    
print "Amount BUGS",bugs







