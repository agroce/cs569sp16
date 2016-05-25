#import os
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

r = random.Random(seed)
sut = sut.sut()
covCount = {}
LCov = None
Stest = None
actCount = 0
ntests = 0
bugs = 0
j = 0

start = time.time()
def randomAction():   
	global actCount,bugs,j,running,actCount
    
	test = False
	for b in xrange(0,depth):
		act = sut.randomEnabled(r)   
#		actCount += 1
		ok = sut.safely(act)
		Scheck = sut.check()
		if len(sut.newBranches()) > 0:
			Stest = sut.state()
			test = True
			
		if (not test) and (LCov != None) and (LCov in sut.currBranches()):
			Stest = sut.start()
			test = True
		actCount += 1
		
		if running:
	        	if sut.newBranches() != set([]):
				print "ACTIONS:", act[0]
            			for b in sut.newBranches():
                			print time.time()-start,len(sut.allBranches()),"New branch",b
				
                    
		if not ok or not Scheck and faults:
			print "FOUND A FAILURE"
			j += 1
			bugs += 1
		        print"Show Fault"
			print "FOUND A FAILURE"
			fault = sut.failure()
			failurename = 'failure' + str(bugs) + '.test'
			sut.saveTest(sut.test(), failurename)
			sut.restart()
def main():				
	global ntests,start
        
	
	while time.time()-start < timeout:
    		if (time.time() > start + timeout):
			break
		
		for ts in xrange(0,width):
			sut.restart()
			ntests += 1
			if (Stest != None ) and (r.random() > 0.7):
				sut.backtrack(Stest)
		
			randomAction()
		
		for b in sut.currBranches():
			if b not in covCount:
				covCount[b] = 0
			covCount[b] += 1
			sortedCov = sorted(covCount.keys(), key = lambda x: covCount[x]) 
			LCov = sortedCov[0]
		
    		if time.time()-start > timeout:
        		print "THE TEST IS STOPPED SINCE TIMEOUT"
        		break 

	sortedCov = sorted(covCount.keys(), key = lambda x: covCount[x])		

	if coverage:
		print"Show Coverage"
        	sut.internalReport()
	
	print ntests,"TOTAL TESTS"    
	print "TOTAL BUGS",bugs
	print "TOTAL ACTIONS",actCount
	print "TOTAL RUNTIME",time.time()-start
if __name__ == '__main__':
	main()
