import os
import random
import argparse
import sut
import sys
import time


#def mutate(test):
   # tcopy = list(test)
   # i = r.randint(0,len(tcopy))
   # sut.replay(tcopy[:i])
    #e = sut.randomEnabled(r)
   # sut.safely(e)
    #trest = [e]
   # for s in tcopy[i+1:]:
    #    if s[1]():
     #       trest.append(s)
      #      sut.safely(s)
    #tcopy = test[:i]+trest
#if len(sut.newCurrBranches()) != 0:
     #   print "NEW BRANCHES DUE TO MUTATION:",sut.newCurrBranches()
    #return tcopy

# check_action():
 ##   global num,actioncount
  #  action = sut.randomEnabled(R)
  #  actioncount += 1
  #  ok = sut.safely(action)
  ##  elapsed = time.time() - start
#if config.running:
   ##     if len(sut.newBranches()) > 0:
    ##        print "ACTION:", action[0]
     #       for b in sut.newBranches():
      #          print elapsed, len(sut.allBranches()),"New branch",b
    




parser = argparse.ArgumentParser()
parser.add_argument("TIMEOUT", type=int, default=60)               #this will take timebudget
parser.add_argument("SEED", type=int, default=None)                    #this will take seed
parser.add_argument("DEPTH", type=int, default=100)                    #this will take depth
parser.add_argument("WIDTH", type=int, default=100)                    #this will take width
parser.add_argument("FAULT_CHECK", type=int, default=0)                #this will take fault check
parser.add_argument("COVERAGE_REPORT", type=int, default=0)            #this will take coverage report
parser.add_argument("DETAIL_OF_RUNNING", type=int, default=0)          #this will take detail of running
#parser.add_argument("INITIAL_POP", type=int, default=0)
X= None
savedTest = None
failureCount = 0
actioncount = 0
testsCovered = []
option = parser.parse_args()               # a object named pointer is made for this 
SEED  = option.SEED
TIMEOUT = option.TIMEOUT
DEPTH = option.DEPTH
WIDTH = option.WIDTH
FAULT_CHECK = option.FAULT_CHECK
COVERAGE_REPORT = option.COVERAGE_REPORT
DETAIL_OF_RUNNING = option.DETAIL_OF_RUNNING
#INITIAL_POP = option.INITIAL_POP
rgen = random.Random()
rgen.seed(SEED)
sut = sut.sut()             #this will reset the system state
start = time.time()         #this will start the system time


if len(sut.newStatements()) > 0:
            savedTest = sut.state()
            storedTest = True
            print "FOUND NEW STATEMENTS",sut.newStatements()



while time.time()-start < TIMEOUT:  
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
                        F = sut.reduce(sut.test(), lambda x: sut.fails(x) or sut.failsCheck(x))
		        Test = prettyListTest(F)				
		        if Test not in testsCovered:
				testsCovered.append(Test)	

		

				print " This is a Reduced Test"

				sut.prettyPrintTest(F)

				failureCount = failureCount + 1       #the failure count will go on increasing

				if (FAULT_CHECK):                              # this will check for the faults
				    name = "failure" + str(failureCount) + ".test"
                                    f = sut.test()
                                    sut.saveTest(F,filename)


				    for (s_reduces) in S:

					    steps_reduce = "#no of steps taken " + str(j)

					    print >> f, sut.prettyName(s_reduces).ljust(80 - len(steps_reduce), ' '), steps_reduce

					    j =j + 1
				    
			else:
	
                                print ""/n
				print "This is the same test"

				sut.prettyPrintTest(F)

				break;

                  
if (COVERAGE_REPORT):
    sut.internalReport()   #printing the result


