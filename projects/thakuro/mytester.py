import os
import random
import argparse
import sut
import sys
import time


def mutate(okTest):
    tcopy = list(test)
    i = rgen.randint(0,len(tcopy))
    e = sut.randomEnabled(rgen)
    sut.safely(e)
    trest = [e]
    for s in tcopy[i+1:]:
        if s[1]():
            trest.append(s)
            sut.safely(s)
    tcopy = test[:i]+trest
    if len(sut.newCurrBranches()) != 0:
        print "NEW BRANCHES DUE TO MUTATION:",sut.newCurrBranches()
    return tcopy

    




parser = argparse.ArgumentParser()
parser.add_argument("TIMEOUT", type=int, default=60)               #this will take timebudget
parser.add_argument("SEED", type=int, default=None)                    #this will take seed
parser.add_argument("DEPTH", type=int, default=100)                    #this will take depth
parser.add_argument("WIDTH", type=int, default=100)                    #this will take width
parser.add_argument("FAULT_CHECK", type=int, default=0)                #this will take fault check
parser.add_argument("COVERAGE_REPORT", type=int, default=0)            #this will take coverage report
parser.add_argument("DETAIL_OF_RUNNING", type=int, default=0)          #this will take detail of running
#parser.add_argument("INITIAL_POP", type=int, default=0)
option = parser.parse_args()               # a object named pointer is made for this 
SEED  = option.SEED
TIMEOUT = option.TIMEOUT
DEPTH = option.DEPTH
WIDTH = option.WIDTH
FAULT_CHECK = option.FAULT_CHECK
COVERAGE_REPORT = option.COVERAGE_REPORT
DETAIL_OF_RUNNING = option.DETAIL_OF_RUNNING
#INITIAL_POP = option.INITIAL_POP
sut = sut.sut()
savedTest = None
RandomMemberSelection = 0
failureCount = 0
actionCount = 0
countCover = {}
leastCover = None
vgoodTest = []
pCheck = 1
okTest = None
bugs = 0
bTest = False
width_actionCount = 0
key = 0
value = 0
pops = []
test = []
rgen = random.Random()
rgen.seed(SEED)
			        #this will reset the system state
start = time.time()         #this will start the system time


while time.time() - start < TIMEOUT:
	sut.restart()
	
	
        for s in xrange(0, WIDTH):                                  #this will go till the width
		action = sut.randomEnabled(rgen)
		yes = sut.safely(action)
		width_actionCount = 1 + width_actionCount
		
		for s in xrange(0, DEPTH):                          #this will go till the depth
			action = sut.randomEnabled(rgen)
			yes = sut.safely(action)
			actionCount = 1+ actionCount


			if (not bTest) and (leastCover<>None) and (leastCover in sut.currStatements()):
				okTest = sut.state()
				vgoodTest.append(okTest)
			if len(sut.newStatements()) > 0:
				okTest = sut.state()
                        	bTest = True
              			print "New Statements Found",sut.newStatements()
			elapsed = time.time() - start
			if DETAIL_OF_RUNNING:
				if sut.newBranches() !=set([]):
					for b in sut.newBranches():
						print elapsed,len(sut.allBranches()),"New Branch",b

			if not yes:
                               

				bugs = bugs + 1
				print"This is a failure"
				print sut.failure()
				F = sut.reduce(sut.test(), sut.fails, True, True)
				sut.prettyPrintTest(F)
				print sut.failure()
				if FAULT_CHECK:
					filename = "failure" + str(bugs) + ".test"
					sut.saveTest(F,filename)

				else:
				    if len(sut.newBranches()) != 0:
					okTest = sut.test()
					mut = mutate(okTest)
					print"", sut.newBranches()
					test.append((list(sut.test()), set(sut.currBranches())))
					test = sorted(test, reverse=True)[:config.width]
					pops.append((mut,sut.currBranches()))
					RandomMembersSelection = random.sample(tests,int(float((len(tests))*.20)))
                        		for x in RandomMembersSelection:
                            			test.remove(x)

				

		
	if COVERAGE_REPORT:
		sut.internalReport()
		mut = mutate(okTest)
		print "\n        ###### Final Report ###### \n"
		print "Number of bugs found: " + str(bugs)
		print "Number of actions: " + str(actionCount)
		print "%s Mutate actions %s" + str(okTest)
		if len(okTest) % 2 != 0:
    			okTest.append(" ")

		split = len(okTest)/2
		l1 = okTest[0:split]
		l2 = okTest[split:]
		for key, value in zip(l1,l2):
  			print '%-20s %s' % (key, value)       
			print "{0:<20s} {1}".format(key, value)
		R = sut.reduce(sut.test(), sut.fails, True, True)
		sut.prettyPrintTest(R)
		print sut.failure()
			
		filename = "failure" + str(bugs) + ".test"
		sut.saveTest(R,filename)

		print "Number of width action count: " + str(width_actionCount)
		print "Total elapsed time: " + str(elapsed)
		print len(sut.allBranches()),"BRANCHES COVERED"
		print len(sut.allStatements()),"STATEMENTS COVERED"
	
		
	if (rgen.random()>pCheck) and (okTest <> None):
		sut.backtrack(okTest)
	        bTest = False

		
	





		



