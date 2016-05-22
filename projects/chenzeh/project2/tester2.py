import sut
import random
import sys
import time

# Terminate the program with time
timeout = int(sys.argv[1])
# Determines the random seed for testing. This should be assigned 0 when using the MEMORY/WIDTH
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
        
        with open(fname,'w+') as f:
            f.write(str(sut.failure())+'\n')
            f.write(str(R)+'\n')


MAX_DEPTH = DEPTH
bugs = 0
elapsed = 0
errors = []
corrects = []

#init variables
rgen = random.Random()
rgen.seed(SEED)
sut = sut.sut()
sut.silenceCoverage()
sut.restart()
states = [sut.state()]


startAll = time.time()


while time.time()-startAll<timeout -2:
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
                    errors.append(sut.currStatements())
                    fault_collection()
                    
                if((len(news)>0)and not(news in errors) and not( news in corrects)):
                    states.append(sut.state())
                    corrects.append(sut.currStatements())

if (COVERAGE_REPORT):
    sut.internalReport()
    
print "TOTAL NUMBER OF BUGS",bugs
