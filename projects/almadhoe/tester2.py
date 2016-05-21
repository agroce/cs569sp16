#******** This code is based on the code writing by Pro. Alex in the class *********

import os
import sut
import random
import sys
import time


def mutate(test):
    tcopy = list(test)
    i = rgen.randint(0,len(tcopy))
    sut.replay(tcopy[:i])
    e = sut.randomEnabled(rgen)
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
    
# For run the code on the command line
timeout = int(sys.argv[1])
Seed = int(sys.argv[2])
depth = int(sys.argv[3])
width = int(sys.argv[4])
faults = int(sys.argv[5])
coverage = int(sys.argv[6])
running = int(sys.argv[7])

rgen = random.Random()
rgen.seed(Seed)

sut = sut.sut()


actCount = 0
bugs = 0
no_tests = 0
tests = []
        
start = time.time()

while time.time()-start < timeout:  
    for ts in xrange(0,width):
        sut.restart()
        no_tests += 1
        for b in xrange(0,depth): 
            act = sut.randomEnabled(rgen)
            actCount += 1
            ok = sut.safely(act)
            propok = sut.check()
            
            #if running=1, print elapsed time, total brach count, new branch if running=0 don't print
            if running == 1:
                if sut.newBranches() != set([]):
                    print "ACTION:",act[0]
                    for b in sut.newBranches():
                        print time.time() - start,len(sut.allBranches()),"New branch",b
            
            #if faults=1, check for bugs and store them in files, if faults=0 don't check for bugs.
            if not ok or not propok:
                if faults == 1:
                    print "FAILURE FOUND.....FAILURES ARE STORING IN FILES"
                    bugs += 1
                    fault = sut.failure()
                    saveFault = 'failure' + str(bugs) + '.test'
                    file = open(saveFault, 'w')
                    print >> file, "Faults: ", fault,"\n"	
                    print >> file, "Test Cases: "
	            for t in sut.test():
	                print >> file, sut.serializable(t)
	            file.close()
	            sut.restart()
	        
	       
	        #Store new branches in tests pool            
            else:
                if len(sut.newBranches()) != 0:
                    tests.append((list(sut.test()), set(sut.currBranches())))
                    
            if rgen.random() > 0.6:    
                m = mutate(sut.test())
                
            else :
                rgen.choice(sut.test()) 
                   
            if (time.time() - start > timeout):
                break                

# if coverage = 1, print internal report            
if coverage == 1:
    sut.internalReport()

print "TOTAL NUMBER OF BUGS",bugs
#print "TOTAL NUMBER OF TESTS",no_tests
#print "TOTAL NUMBER OF ACTIONS",actCount
print "TOTAL NUMBER OF RUNTIME",time.time()-start
