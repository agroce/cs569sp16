import os, sys, sut, time, random

def collectCoverage():
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
    if running:
        if sut.newBranches() != set([]):
            for b in sut.newBranches():
                print time.time()-start,len(sut.allBranches()),"New branch",b
            sawNew = True
        else:
            sawNew = False    
                    
    if not ok or not check:
        if faults:
            bugs += 1
            fail.append(sut.test())
            collectCoverage()
            R = sut.reduce(sut.test(),sut.failpool, True, True)
            sut.restart()
            print "FOUND A FAILURE"
            fault = sut.failure()
            fname = 'failure' + str(bugs) + '.test'
            wfile = open(fname, 'w+')
            wfile.write(str(fault))
            wfile.close() 
            sut.restart() 
           
    else:
        if len(sut.newBranches()) != 0:
            print "FOUND NEW BRANCHES",sut.newBranches()
            tests.append((list(sut.test()), set(sut.currBranches())))    
    return ok
	
timeout = int(sys.argv[1]) #you can use 60 as a default number 
seed = int(sys.argv[2])    #1
depth = int(sys.argv[3])   #100
width = int(sys.argv[4])   #1
faults = int(sys.argv[5])  #0
coverage = int(sys.argv[6])#1
running = int(sys.argv[7]) #1
rgen = random.Random(seed)

sut = sut.sut()
coverageCount = {}
tests = []
collect = []
fail = []
belowMean = set([])

bugs = 0
actCount = 0
budget1 = 20
budget2 = 20

print "STARTING PHASE 1: COLLECTE COVERAGE"
start = time.time()
ntests = 0
while time.time()-start < budget1:
    for ts in xrange(0,width):
        sut.restart()
        ntests += 1
        for b in xrange(0,depth):
            if not randomAction():
                break    
        collectCoverage()

print "STARTING PHASE 2: ANALYSIS COVERAGE"        
start = time.time()
while time.time()-start < budget2:
    sortedcoverage = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])
    coverageSum = sum(coverageCount.values())
    try:
        coverageMean = coverageSum / (float(len(coverageCount)))
    
    except Zero_Division_Error:
        print ("NO BRANCHES COLLECTED")  
          
    for b1 in sortedcoverage:
        if coverageCount[b1] < coverageMean:
                belowMean.add(b1)
        else:
            break            
        print len(belowMean),"Branches BELOW MEAN COVERAGE OUT OF",len(coverageCount) 
                  
    if time.time()-start > timeout:
        print "THE TEST STOP SINCE TIMEOUT"
        break 
                           
if coverage:
    sut.internalReport()

print "TOTAL BUGS",bugs
print "TOTAL TESTS",ntests
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-start