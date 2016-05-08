import os
import sut
import random
import sys
import time

# To generate random tests and find bugs if faults = 1
def randomAction():   
    global actCount, bugs, fails
    sawNew = False
    act = sut.randomEnabled(rgen)
    #tryStutter = (act != None) and (act[1]())
    actCount += 1
    ok = sut.safely(act)
    propok = sut.check()
   
    #if running=1, print elapsed time, total brach count, new branch otherwise don't print
    if running:
        if sut.newBranches() != set([]):
        #print "ACTION:",act[0],tryStutter
            for b in sut.newBranches():
                print time.time()-start,len(sut.allBranches()),"New branch",b
            sawNew = True
        else:
            sawNew = False    
                    
    #if faults=1, check for bugs, otherwise don't check for bugs.
    if not ok or not propok:
        if faults:
            bugs += 1
            fail.append(sut.test())
            saveCover()
            R = sut.reduce(sut.test(),sut.fails, True, True)
            #sut.prettyPrintTest(R)
            sut.restart()
            print "FAILURE FOUND.....FAILURES ARE STORING IN FILES"
            fault = sut.failure()
            fname = 'failure' + str(bugs) + '.test'
            wfile = open(fname, 'w+')
            wfile.write(str(fault))
            wfile.close() 
            sut.restart() 
     
    #Store new branches in tests pool            
    else:
        if len(sut.newBranches()) != 0:
            print "NEW BRANCHES FOUND",sut.newBranches()
            tests.append((list(sut.test()), set(sut.currBranches())))    
    return ok 
            

# To save the current branches
def saveCover():
    global covCount
    for b in sut.currBranches():
        if b not in covCount:
            covCount[b] = 0
        covCount[b] += 1


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
collect = []
fail = []
belowMean = set([])

budget = 30
budget2 = 30
actCount = 0
bugs = 0
no_tests = 0


print "PHASE 1: GATHER COVERAGE"

start = time.time()

#elapsed = time.time()-start
while time.time()-start < budget:
    for ts in xrange(0,width):
        sut.restart()
        no_tests += 1
        for b in xrange(0,depth):
            if not randomAction():
                break    
        saveCover()

print "PHASE 2: ANALYSIS COVERAGE"
        
start = time.time()
while time.time()-start < budget2:
    sortedCov = sorted(covCount.keys(), key=lambda x: covCount[x])
    
    covSum = sum(covCount.values())
    try:
        covMean = covSum / (float(len(covCount)))
    
    except ZeroDivisionError:
        print ("WARNING: NO BRANCHES COLLECTED")  
          
    for b1 in sortedCov:
        if covCount[b1] < covMean:
                belowMean.add(b1)
        else:
            break
            
        print len(belowMean),"Branches BELOW MEAN COVERAGE OUT OF",len(covCount) 

    
    #  Stop testing when the specified time has finished                   
    if time.time()-start > timeout:
        print "THE TEST IS STOPPED DUE TO TIMEOUT"
        break 
                  
# if coverage = 1, print internal report            
if coverage:
    sut.internalReport()
    

print "TOTAL NUMBER OF BUGS",bugs
print "TOTAL NUMBER OF TESTS",no_tests
print "TOTAL NUMBER OF ACTIONS",actCount
print "TOTAL NUMBER OF RUNTIME",time.time()-start
            
        
        
        
        
        