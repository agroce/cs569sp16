import os
import sys
import sut
import time
import random

			
# To save the current branches
def saveCover():
    global coverageCount
    for b in sut.currBranches():
        if b not in coverageCount:
            coverageCount[b] = 0
        coverageCount[b] += 1

def randomAction():   
    global actCount, bugs, failpool
    sawNew = False
    act = sut.randomEnabled(rgen)   
    actCount += 1
    ok = sut.safely(act)
    check = sut.check()
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
    if not ok or not check:
        if faults:
            bugs += 1
            fail.append(sut.test())
            saveCover()
            R = sut.reduce(sut.test(),sut.failpool, True, True)
            #sut.prettyPrintTest(R)
            sut.restart()
            print "FOUND A FAILURE"
            fault = sut.failure()
            fname = 'failure' + str(bugs) + '.test'
            wfile = open(fname, 'w+')
            wfile.write(str(fault))
            wfile.close() 
            sut.restart() 
     
    #Store new branches in tests pool            
    else:
        if len(sut.newBranches()) != 0:
            print "FOUND NEW BRANCHES",sut.newBranches()
            tests.append((list(sut.test()), set(sut.currBranches())))    
    return ok 

timeout = int(sys.argv[1])
seed = int(sys.argv[2])
depth = int(sys.argv[3])
width = int(sys.argv[4])
faults = int(sys.argv[5])
coverage = int(sys.argv[6])
running = int(sys.argv[7])

rgen = random.Random(seed)

sut = sut.sut()
coverageCount = {}
tests = []
collect = []
fail = []
belowMean = set([])

budget1 = 20
budget2 = 20
actCount = 0
bugs = 0
no_tests = 0

print "STARTING PHASE 1: GATHER COVERAGE"

start = time.time()
while time.time()-start < budget1:
    for ts in xrange(0,width):
        sut.restart()
        no_tests += 1
        for b in xrange(0,depth):
            if not randomAction():
                break    
        saveCover()
print "STARTING PHASE 2: ANALYSIS COVERAGE"
        
start = time.time()
while time.time()-start < budget2:
    sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])
    covSum = sum(coverageCount.values())
    try:
        covMean = covSum / (float(len(coverageCount)))
    
    except ZeroDivisionError:
        print ("WARNING: NO BRANCHES COLLECTED")  
          
    for b1 in sortedCov:
        if coverageCount[b1] < covMean:
                belowMean.add(b1)
        else:
            break            
        print len(belowMean),"Branches BELOW MEAN COVERAGE OUT OF",len(coverageCount) 
                  
    if time.time()-start > timeout:
        print "THE TEST IS STOPPED SINCE TIMEOUT"
        break 
                           
if coverage:
    sut.internalReport()
    
print "TOTAL BUGS",bugs
print "TOTAL TESTS",no_tests
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-start
          
