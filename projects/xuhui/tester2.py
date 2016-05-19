import os
import sys
import sut
import time
import random

timeout = int(sys.argv[1])
seed = int(sys.argv[2])
depth = int(sys.argv[3])
width = int(sys.argv[4])
faults = int(sys.argv[5])
coverage = int(sys.argv[6])
running = int(sys.argv[7])

def collectCoverage():
    global coverageCount
    for b in sut.currBranches():
        if b not in coverageCount:
            coverageCount[b] = 0
        coverageCount[b] = coverageCount[b] + 1

def randomAction():   
    global actCount, bugs, errorpool
    sawNew = False
    act = sut.randomEnabled(rgen)   
    actCount += 1
    ok = sut.safely(act)
    if running:
        if sut.newBranches() != set([]):
            for b in sut.newBranches():
                print time.time()-start,len(sut.allBranches()),"New branch",b
            sawNew = True
        else:
            sawNew = False    
                    
    if not ok:
		bugs += 1
		print "FOUND A FAILURE"
                if faults:
			print"Show Fault"
			print sut.failure()
                        error.append(sut.test())
                        collectCoverage()
                        R = sut.reduce(sut.test(),sut.errorpool, True, True)
                        sut.prettyPrintTest(R)
                        sut.restart()
			
                        print "FOUND A FAILURE"
                        fault = sut.failure()
                        failurename = 'failure' + str(bugs) + '.test'
                        wfile = open(failurename, 'w+')
                        wfile.write(str(fault))
                        wfile.close() 
                        sut.restart() 
                
                else:
                    if len(sut.newBranches()) > 0:
                        print "FOUND NEW BRANCHES",sut.newBranches()
                        tests.append((list(sut.test()), set(sut.currBranches())))    
                return ok 

def belowmean():
	global belowMean
	sortedCoverage = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])
	coverageSum = sum(coverageCount.values())
	try:
		coverageMean = coverageSum / (1.0*(len(coverageCount)))
	except Zero_Division_Error:
		print ("NO BRANCHES COLLECTED")  
	for b1 in sortedCoverage:
		if coverageCount[b1] < coverageMean:
				belowMean.add(b1)
		else:
			break            
		print len(belowMean),"Branches BELOW MEAN COVERAGE OUT OF",len(coverageCount) 
				
rgen = random.Random(seed)

sut = sut.sut()
coverageCount = {}
tests = []
collect = []
error = []
belowMean = set([])

actCount = 0
bugs = 0
ntests = 0


print "STARTING PHASE 1: GATHER COVERAGE"
start = time.time()
while time.time()-start < timeout:
    for ts in xrange(0,width):
        if (time.time() > start + timeout):
            break
        sut.restart()
        ntests += 1
        for b in xrange(0,depth):
            if (time.time() > start + timeout):
                break
            if not randomAction():
                break    
        collectCoverage()
		
print "STARTING PHASE 2: ANALYSIS COVERAGE"        
start = time.time()
while time.time()-start < timeout:
    if (time.time() > start + timeout):
        break
	belowmean()                  
    if time.time()-start > timeout:
        print "THE TEST IS STOPPED SINCE TIMEOUT"
        break 
                           
if coverage:
	print"Show Coverage"
        sut.internalReport()
	
print ntests,"TOTAL TESTS"    
print "TOTAL BUGS",bugs
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-start