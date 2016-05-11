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


timeout = int(sys.argv[1])
seed = int(sys.argv[2])
depth = int(sys.argv[3])
width = int(sys.argv[4])
faults = int(sys.argv[5])
coverage = int(sys.argv[6])
running = int(sys.argv[7])

rgen = random.Random(seed)

sut = sut.sut()
sut.silenceCoverage()

covCount = {}
tests = []
collect = []
fail = []
belowMean = set([])

actCount = 0
bugs = 0
no_tests = 0

global fails
        
start = time.time()

while time.time()-start < timeout:  
    saveCover()  
    for ts in xrange(0,width):
        sut.restart()
        no_tests += 1
        for b in xrange(0,depth): 
            act = sut.randomEnabled(rgen)
            actCount += 1
            ok = sut.safely(act)
            propok = sut.check()
            #saveCover()  
        
    #if faults=1, check for bugs, otherwise don't check for bugs.
            if not ok or not propok:
                if faults == 1:
                    bugs += 1
                    saveCover()
                    #R = sut.reduce(sut.test(),sut.fails, True, True)
                    #sut.prettyPrintTest(R)
                    #sut.restart()
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
                    print "NEW BRANCHES FOUND",sut.newBranches()
                    tests.append((list(sut.test()), set(sut.currBranches())))    
                        
            #if running=1, print elapsed time, total brach count, new branch otherwise don't print
            if running == 1:
                if sut.newBranches() != set([]):
                    print "ACTION:",act[0]
                    #elapsed1 = time.time() - start
                    for b in sut.newBranches():
                        print time.time() - start,len(sut.allBranches()),"New branch",b
            
        
        saveCover()   
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
        saveCover() 
        for (t,c) in tests:
            if b1 in belowMean:
                collect.append((t,c))
                break
        
                
        sut.restart()
        if rgen.random() > 0.9:
            sut.backtrack(test)
            #print len(sut.state())
            #sut.replay(rgen.choice(collect)[0]) 
        if time.time()-start > timeout:
            break 
        else:
            sut.restart()
            
print len(belowMean),"BRANCHES BELOW AVERAGE COVERAGE OUT OF",len(covCount)         
                  
                  
# if coverage = 1, print internal report            
if coverage == 1:
    sut.internalReport()
    

print "TOTAL NUMBER OF BUGS",bugs
print "TOTAL NUMBER OF TESTS",no_tests
print "TOTAL NUMBER OF ACTIONS",actCount
print "TOTAL NUMBER OF RUNTIME",time.time()-start

        
        
        