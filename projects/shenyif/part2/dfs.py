import sut
import random
import sys
import time

TIME_BUDGET = int(sys.argv[1])
SEED = int(sys.argv[2])
DEPTH = int(sys.argv[3])
WIDTH = int(sys.argv[4])
FAULT_CHECK = int(sys.argv[5])
COVERAGE_REPORT = int(sys.argv[6])
RUNNING_DETAIL = int(sys.argv[7])

rgen = random.Random()
MAX_DEPTH = DEPTH 

bugs = 0

sut = sut.sut()
sut.silenceCoverage()
sut.restart()


visited = []
test = []

S = []
S.append((sut.state(),[]))

startAll = time.time()


while S != []:
    
    (v, test) = S.pop()
    sut.backtrack(v)
    
    if (v not in visited) and (len(test) < MAX_DEPTH):
        
        visited.append(v)
        trans = sut.enabled()
        rgen.shuffle(trans)
        
        for (name, guard, act) in trans:
            
                test.append(name)
                
                ok = sut.safely((name, guard, act))
                
                if not ok:
                    
                    bugs += 1
                    print "use"+str(time.time()-startAll)
                    print "FOUND A LARGE FAILURE"
                    print sut.failure()
                    print "REDUCING"
                    R = sut.reduce(sut.test(),sut.fails, True, True)
                    sut.prettyPrintTest(R)
                    print sut.failure()
                
                S.append((sut.state(),test))


print bugs,"FAILED"


