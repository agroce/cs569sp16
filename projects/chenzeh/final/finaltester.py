
## This version is my last result demons, This version 
## based on last two projects and add mutation function
## and crosscover

## Zehuan Chen

import sut
import random
import sys
import time


# Terminate condition:
# Time limit is restrict
timeout = int(sys.argv[1])
# Random seed for generating test cases.
# This should be assigned 0 when using the MEMORY/WIDTH

SEED = int(sys.argv[2])
# TEST_LENGTH or Depth
DEPTH = int(sys.argv[3])
WIDTH = int(sys.argv[4])
# Enable/Disable Faults
FAULT_CHECK = int(sys.argv[5])
# Enable/Disable Coverage
COVERAGE_REPORT = int(sys.argv[6])
# Enable/Disable Running
RUNNING= int(sys.argv[7])


MAX_DEPTH = DEPTH
bugs = 0
elapsed = 0
bestNum = 20
errors = []
corrects = []
population = []


#function to record the infromation about branches and statements
def run_collection():
    if  RUNNING:
        
        if sut.newBranches() != set([]):
            
            print "ACTION:",action[0]
            for b in sut.newBranches():
                print elapsed,len(sut.allBranches()),"New branch",b
            sawNew = True
        else:
            sawNew = False
            
        if sut.newStatements() != set([]):
            
            print "ACTION:",action[0]
            for s in sut.newStatements():
                print elapsed,len(sut.allStatements()),"New statement",s
            sawNew = True
        else:
            sawNew = False


#function to collect the error information
def fault_collection():
    
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
        


#mutation function
def mutate(test):
    
    global bugs
    tcopy = list(test)
    #randomly choose part of the chosen case
    i = rgen.randint(0,len(tcopy))
    #replay to be the chosen state
    sut.replay(tcopy[:i],catchUncaught = True)
    e = sut.randomEnabled(rgen)
    #check whether it is correct
    ok = sut.safely(e)
    
    if not ok:
       bugs = bugs+1
       errors.append(sut.currStatements())
       fault_collection()

    trest = [e]

    for s in tcopy[i+1:]:
        if s[1]():
            trest.append(s)
            sut.safely(s)
    tcopy = test[:i]+trest
    
    #if we find new branches
    if len(sut.newCurrBranches()) != 0:
        print "NEW BRANCHES DUE TO MUTATION:",sut.newCurrBranches()
    return tcopy


#function to do the crossover
def crossover(test,test2):
    
    global bugs
    tcopy = list(test)
    #randomly choose part of test
    i = rgen.randint(0,len(tcopy))
    #replay to be the chosen state
    sut.replay(tcopy[:i],catchUncaught = True)
    
    trest = []

    for s in test2[i:]:
        if s[1]():
            
            trest.append(s)
            #check whether it is correct
            ok = sut.safely(s)
            
            if not ok:
                bugs = bugs+1
                errors.append(sut.currStatements())
                fault_collection()

    #to do crossover
    tcopy = test[:i]+trest

    #if we find new branches
    if len(sut.newCurrBranches()) != 0:
        print "NEW BRANCHES DUE TO CROSSOVER:",sut.newCurrBranches()
    return tcopy



#init variables
rgen = random.Random()
rgen.seed(SEED+1)
sut = sut.sut()
sut.silenceCoverage()
sut.restart()
states = [sut.state()]
startAll = time.time()

#phase 1, we use the BFS random test.
while time.time()-startAll<timeout/2.:
    for s in states:
        elapsedTime = time.time()-startAll
        
        if elapsedTime>=timeout:
            break
        
        sut.restart()
        sut.backtrack(s)

        for w in xrange(0,WIDTH):
            # based on depth randomly test
            for d in xrange(0,MAX_DEPTH):
                
                if (time.time()-startAll)>timeout:
                    break
                
                action = sut.randomEnabled(rgen)
                ok = sut.safely(action)
                elapsed = time.time() - startAll
                run_collection()
                news = sut.newStatements()

                if not ok:
                    bugs = bugs+1
                    errors.append(sut.currStatements())
                    fault_collection()
                    
                if((len(news)>0)and not(news in errors) and not( news in corrects)):
                    states.append(sut.state())
                    corrects.append(sut.currStatements())

        # record needed information for the next two phases
        population.append((list(sut.test()),set(sut.currBranches())))


#phase 2, we use the mutate function
while time.time()-startAll<timeout*0.75:
    
    if time.time()-startAll>timeout:
        break

    #use sort function to choose the best bestNum cases
    sortPop = sorted(population,key = lambda x: len(x[1]),reverse=True)
    (t,b) = rgen.choice(sortPop[:bestNum])
    m = mutate(t)
    population.append((m,sut.currBranches()))


#phase 3, we use the crossover function
while time.time()-startAll<timeout:
    
    if time.time()-startAll>timeout:
        break

    #use sort function to choose the best bestNum cases
    sortPop = sorted(population,key = lambda x: len(x[1]),reverse=True)
    (t,b) = rgen.choice(sortPop[:bestNum])
    (t2,b) = rgen.choice(sortPop[:bestNum])
    m = crossover(t,t2)
    population.append((m,sut.currBranches()))



if (COVERAGE_REPORT):
    sut.internalReport()
    
print "TOTAL NUMBER OF BUGS",bugs






