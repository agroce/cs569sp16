import sut
import random
import sys
import time

timeout = int(sys.argv[1])
SEED = int(sys.argv[2])
DEPTH = int(sys.argv[3])
WIDTH = int(sys.argv[4])
FAULT_CHECK = int(sys.argv[5])
COVERAGE_REPORT = int(sys.argv[6])
RUNNING= int(sys.argv[7])

rgen = random.Random()
rgen.seed(SEED)
MAX_DEPTH = DEPTH 

bugs = 0
elapsed = 0
visited = []
test = []
layer =WIDTH

sut = sut.sut()
sut.silenceCoverage()
sut.restart()

S = []
S.append((sut.state(),[]))


startAll = time.time()
    
while S != []  :
    
    elapsedTime = time.time()-startAll
    if elapsedTime>=timeout:
        break
    
    (v, test) = S.pop()
    sut.backtrack(v)
    
    if (v not in visited) and (len(test) < MAX_DEPTH):
        
        visited.append(v)
        trans = sut.enabled()
        rgen.shuffle(trans)
        
        for (name, guard, act) in trans:
            
                test.append(name)
                
                ok = sut.safely((name, guard, act))
                propok = sut.check()

                
                if not ok or not propok:
                    
                    bugs += 1
                    
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
                
                S.append((sut.state(),test))

                if RUNNING:
                    if sut.newBranches() != set([]):
                        #print "ACTION:",a[0],tryStutter
                        #  print "ACTION:",a[0],tryStutter
                        for b in sut.newBranches():
                            print time.time()-startAll,len(sut.allBranches())," new branch",b
                        new = True
                    else:
                        new = False



if (COVERAGE_REPORT):
    sut.internalReport()
print "TOTAL NUMBER OF BUGS",bugs
