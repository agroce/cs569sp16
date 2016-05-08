#******** This code is modified version of newCover.py which written by Pro. Alex *********

import os
import sut
import random
import sys
import time


# To save the current branches
def saveCover():
    global covCount
    for b in sut.currBranches():
        if b not in covCount:
            covCount[b] = 0
        covCount[b] += 1

# For run the code on the command line
timeout = int(sys.argv[1])
seed = int(sys.argv[2])
depth = int(sys.argv[3])
width = int(sys.argv[4])
faults = int(sys.argv[5])
coverage = int(sys.argv[6])
running = int(sys.argv[7])

rgen = random.Random(seed)

sut = sut.sut()

covCount = {}
tests = []
belowMean = set([])

actCount = 0
bugs = 0
no_tests = 0

global fails
        
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
            
            #if faults=1, check for bugs, if faults=0 don't check for bugs.
            if not ok or not propok:
                if faults == 1:
                    bugs += 1
                    saveCover()
                    print "FAILURE FOUND.....FAILURES ARE STORING IN FILES"
                    fault = sut.failure()
                    fname = 'failure' + str(bugs) + '.test'
                    wfile = open(fname, 'w')
                    wfile.write(str(fault))
                    wfile.close() 
                    sut.restart() 
     
            #Store new branches in tests pool            
            else:
                if len(sut.newBranches()) != 0:
                    test = sut.state()
                    #print "NEW BRANCHES FOUND",sut.newBranches()
                    tests.append((list(sut.test()), set(sut.currBranches())))    
    
            
        saveCover()
           
        sortedCov = sorted(covCount.keys(), key=lambda x: covCount[x])
        covSum = sum(covCount.values())
        
        try:
            covMean = covSum / (float(len(covCount)))
    
        except ZeroDivisionError:
            print ("WARNING: NO BRANCHES COLLECTED")  
          
        for b in sortedCov:
            if covCount[b] < covMean:
                belowMean.add(b)
            else:
                break
        saveCover() 
         
        sut.restart()
        if rgen.random() > 0.9:
            sut.backtrack(test)
            
        no_tests += 1
        for b in xrange(0,depth):
            if not ok or not propok:
                if faults == 1:
                    bugs += 1
                    saveCover()
                    print "FAILURE FOUND.....FAILURES ARE STORING IN FILES"
                    fault = sut.failure()
                    fname = 'failure' + str(bugs) + '.test'
                    wfile = open(fname, 'w')
                    wfile.write(str(fault))
                    wfile.close() 
                    sut.restart() 
     
        saveCover()
            
# if coverage = 1, print internal report            
if coverage == 1:
    sut.internalReport()

print "TOTAL NUMBER OF BUGS",bugs
print "TOTAL NUMBER OF TESTS",no_tests
print "TOTAL NUMBER OF ACTIONS",actCount
print "TOTAL NUMBER OF RUNTIME",time.time()-start
