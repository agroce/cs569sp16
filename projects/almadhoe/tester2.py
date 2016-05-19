#******** Some code has taken from newCover.py which written by Pro. Alex *********

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
Exp = set([])
fail = []

actCount = 0
bugs = 0
no_tests = 0
        
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
                    i = 0
                    print "FAILURE FOUND.....FAILURES ARE STORING IN FILES"
                    bugs += 1
                    saveCover()
                    fault = sut.failure()
                    saveFault = 'failure' + str(bugs) + '.test'
                    file = open(saveFault, 'w')
                    print >> file, "Faults:", fault,"\n"	
                    print >> file, "********************************* Test Cases: ******************************************"
	            for t in sut.test():
	                print >> file, sut.serializable(t)
	            file.close()
	            sut.restart()
	            
            if (time.time() - start > timeout):
			    break     
     
            #Store new branches in tests pool            
            else:
                if len(sut.newBranches()) != 0:
                    test = sut.state()
                    tests.append((list(sut.test()), set(sut.currBranches())))    
    
            
        saveCover()
        # Sort coverage dictionary   
        sortedCov = sorted(covCount.keys(), key=lambda x: covCount[x])
        covSum = sum(covCount.values())
        
        #Calculate the mean for coverage
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
        
        #For probability  
        exp = 1 - (len(belowMean) / len(covCount))
        
        if rgen.random() > exp:
            sut.backtrack(test)
    
        #if faults=1, check for bugs and store them in files, if faults=0 don't check for bugs.    
        if not ok or not propok:
                if faults == 1:
                    i = 0
                    print "FAILURE FOUND.....FAILURES ARE STORING IN FILES"
                    bugs += 1
                    saveCover()
                    fault = sut.failure()
                    saveFault = 'failure' + str(bugs) + '.test'
                    file = open(saveFault, 'w')
                    print >> file, "Faults:", fault,"\n"	
                    print >> file, "********************************* Test Cases: ******************************************"
	            for t in sut.test():
	                print >> file, sut.serializable(t)
	            file.close()
	            sut.restart()
	            
        if (time.time() - start > timeout):
			break     
     
        #Store new branches in tests pool            
        else:
                if len(sut.newBranches()) != 0:
                    tests.append((list(sut.test()), set(sut.currBranches())))     
                
        saveCover()     
    
            
# if coverage = 1, print internal report            
if coverage == 1:
    sut.internalReport()

print "TOTAL NUMBER OF BUGS",bugs
print "TOTAL NUMBER OF TESTS",no_tests
print "TOTAL NUMBER OF ACTIONS",actCount
print "TOTAL NUMBER OF RUNTIME",time.time()-start
