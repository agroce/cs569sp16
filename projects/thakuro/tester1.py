
import os
import random
import argparse
import sut
import sys
import time



parser = argparse.ArgumentParser()
parser.add_argument("TIMEOUT", type=int, default=60)               #this will take timebudget
parser.add_argument("SEED", type=int, default=None)                    #this will take seed
parser.add_argument("DEPTH", type=int, default=100)                    #this will take depth
parser.add_argument("WIDTH", type=int, default=100)                    #this will take width
parser.add_argument("FAULT_CHECK", type=int, default=0)                #this will take fault check
parser.add_argument("COVERAGE_REPORT", type=int, default=0)            #this will take coverage report
parser.add_argument("DETAIL_OF_RUNNING", type=int, default=0)          #this will take detail of running
X= None
savedTest = None
failureCount = 0
testsCovered = []
option = parser.parse_args()               # a object named pointer is made for this 
SEED  = option.SEED
TIMEOUT = option.TIMEOUT
DEPTH = option.DEPTH
WIDTH = option.WIDTH
FAULT_CHECK = option.FAULT_CHECK
COVERAGE_REPORT = option.COVERAGE_REPORT
DETAIL_OF_RUNNING = option.DETAIL_OF_RUNNING
rgen = random.Random()
rgen.seed(SEED)
sut = sut.sut()             #this will reset the system state
start = time.time()         #this will start the system time
while time.time()-start < TIMEOUT:  
    sut.restart()
    for f in xrange(0,DEPTH):
	action = sut.randomEnabled(rgen)
        for f in xrange(0,WIDTH):
		action = sut.randomEnabled(rgen)
		if(DETAIL_OF_RUNNING):	
        		elapsed = time.time() - start    #Calculating the time
			if sut.newBranches() != set([]):
				print "ACTION:",action[0]
				for b in sut.newBranches():
					print elapsed,len(sut.allBranches()),"This is a branch",b   #this will go through all the new branches and print them
        ok = sut.safely(action)	
	if not ok:
	
		X = sut.reduce(sut.test())			
		if X not in testsCovered:

			testsCovered.append(X)		
	
			print " This is a Reduced Test"

			sut.prettyPrintTest(X)

                        failureCount = failureCount + 1       #the failure count will go on increasing

			if (FAULT_CHECK):                     # this will check for the faults

                             for (s_reduces) in S:

				    steps_reduce = "#no of steps taken " + str(j)

				    print >> f, sut.prettyName(s_reduces).ljust(80 - len(steps_reduce), ' '), steps_reduce

				    j =j + 1
			    
		else:	

			print "This is the same test"

			sut.prettyPrintTest(S)

			break;

                  
if (COVERAGE_REPORT):
    sut.internalReport()   #printing the result
