import sut
import sys
import time
import random

timeout = int(sys.argv[1])
seed = int(sys.argv[2])
depth = int(sys.argv[3])
width = int(sys.argv[4])
faults = int(sys.argv[5])
coverage = int(sys.argv[6])
running = int(sys.argv[7])    

actCount = 0
bugs = 0
ntests = 0
j = 0

covCount = {}
LCov= None
Stest = None
sut = sut.sut()
rgen = random.Random(seed)

start = time.time()
def loopBug():
    global Stest,rgen,sut,depth,LCov,actCount,running,faults,j,bugs
    if Stest != None:
        if rgen.random() > 0.4:
            sut.backtrack(Stest)
    test = False  
    for s in xrange(0,depth):
            act = sut.randomEnabled(rgen)
            ok = sut.safely(act)
 
            if len(sut.newBranches()) > 0:
                Stest = sut.state()
                test = True
                
            if (not test):
				if (LCov!= None):
					if (LCov in sut.currBranches()):
						Stest = sut.state()
						test = True
            
            actCount += 1 
            if running == 1:
                if sut.newBranches() != set([]):
                    print "ACTION:",act[0]
                    for b in sut.newBranches():
                        print time.time() - start,len(sut.allBranches()),"New branch",b
            
            if faults == 1:
                if not ok:
                    print "Found FAILURES and It IS STORING IN FILES:"
                    j += 1
                    bugs += 1
                    fault = sut.failure()
                    failurename = 'failure' + str(bugs) + '.test' 
                    sut.saveTest(sut.test(), failurename)
                    print "The bug's number found is" ,j
                    sut.restart()

def main():
    global ntests
    while time.time()-start < timeout:
        for ts in xrange(0,width):
            sut.restart()
            ntests += 1
              
            loopBug()
          
            for s in sut.currBranches():
                if s not in covCount:
                    covCount[s] = 0
                covCount[s] += 1    
                sortedCov = sorted(covCount.keys(), key=lambda x: covCount[x])
                LCov= sortedCov[0]
        
            if (time.time() - start > timeout):
				print "THE TEST IS STOPPED SINCE TIMEOUT"
                                break
				
    sortedCov = sorted(covCount.keys(), key=lambda x: covCount[x])
    if coverage == 1:
	print "SHOW COVERAGE"
        sut.internalReport()
	
	print ntests, "TOTAL TESTS"
    print "TOTAL BUGS",bugs
    print "TOTAL ACTIONS",actCount
    print "TOTAL RUNNINGTIME",time.time()-start

if __name__ == '__main__':
    main()
