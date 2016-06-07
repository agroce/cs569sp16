import sut
import random
import sys
import time
import argparse

parser = argparse.ArgumentParser(description='My Tester, the argument must be specified in this order: "python mytester.py timeout seeds depth width Faults Coverage Running"')
parser.add_argument('-t','--timeout', type=int, nargs='?', default=60, help='Timeout will be parsed in seconds - The default value is 60 seconds')
parser.add_argument('-s','--seeds', type=int, nargs='?', default=0, help=' The number of seeds required. The default value is 0')
parser.add_argument('-d','--depth', type=int, nargs='?', default=100, help='The depth of each test case. The default is 100')
parser.add_argument('-l','--width', type=int, nargs='?', default=100, help='The length/Memory. The default value is 100')
parser.add_argument('-f','--FaultsEnabled', type=bool, nargs='?', default=False, help='Save Test Case when Failure is discovered. The default value is False')
parser.add_argument('-c','--CoverageEnabled', type=bool, nargs='?', default=False, help='Report Code coverage. The default value is False')
parser.add_argument('-r','--RunningEnabled', type=bool, nargs='?', default=False, help='Check Coverage on the fly while running. The default value is False')
parser.add_argument('-a','--algorithm', type=str, nargs='?', default='var', help='There are 2 Algorithms. [var] is a Random algorithm based on sepcified propability and [test] is random algorithm concentrate on a group of actions for automatically assigned depths based on the length of enabled actions. The default algorithm is prop')

arguments = parser.parse_args()

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def prettyListTest(test, columns=30):
        i = 0	
	actionsList = []
        for (s,_,_) in test:
	    parameters = 0
            steps = "# STEP " + str(i)
	    #print "each", sut.prettyName(s)
	    if "." in sut.prettyName(s):
		statement = sut.prettyName(s).split(".",1)[1]
		#print "statement", statement
	    	methodName = find_between("."+statement, ".", "(")
		#print "methodName", methodName
		if find_between(statement, "(", ")") != "":
			parameters = find_between(statement, "(", ")").count(",") + 1
			#print "count", parameters
		#print "parameter", parameters
	    else:
		methodName = "A"
            #actionsList.append(sut.prettyName(s).ljust(columns - len(steps),' '))
	    actionsList.append(methodName + "-" + str(parameters))
            i += 1
	return actionsList


testsCovered = []
S= None
savedTest = None
failureCount = 0

TIME_BUDGET = arguments.timeout

SEED = arguments.seeds

DEPTH = arguments.depth

WIDTH = arguments.width

FAULT_CHECK =  arguments.FaultsEnabled

COVERAGE_REPORT =  arguments.CoverageEnabled

RUNNING_DETAIL =  arguments.RunningEnabled

ALGORITHM = arguments.algorithm

rgen = random.Random()
rgen.seed(SEED)
count = 0
sut = sut.sut()
#sut.silenceCoverage()

if (ALGORITHM == 'var'):
	start1 = time.time()
	while time.time()-start1 < TIME_BUDGET:
	    sut.restart()
	    for s in xrange(0,DEPTH):
		action = sut.randomEnabled(rgen)
		if(RUNNING_DETAIL):	
			elapsed = time.time() - start1
			if sut.newBranches() != set([]):
				print "ACTION:",action[0]
				for b in sut.newBranches():
					print elapsed,len(sut.allBranches()),"New branch",b
		ok = sut.safely(action)	
		if (not ok):		
			S = sut.reduce(sut.test(), lambda x: sut.fails(x) or sut.failsCheck(x))			
			if S not in testsCovered:
				testsCovered.append(S)
				print "------------------------------------------"+ "\n"			
				print "Reduced Test"
				sut.prettyPrintTest(S)
				failureCount += 1
				if (FAULT_CHECK):
				    f = open("failure_file" + str(failureCount) + ".test", "w")
				    j = 0
			       	    for (s_reduces, _, _) in S:
					    steps_reduce = "# STEP " + str(j)
					    print >> f, sut.prettyName(s_reduces).ljust(80 - len(steps_reduce), ' '), steps_reduce
					    j += 1
				    f.close()
			else:
				print "------------------------------------------"+ "\n"	
				print "Same test"
				sut.prettyPrintTest(S)
				break;


else:
	start2 = time.time()
	while time.time()-start2 < TIME_BUDGET:
	    sut.restart()
	    for s in xrange(0,DEPTH):
		action = sut.randomEnabled(rgen)
		if(RUNNING_DETAIL):	
			elapsed = time.time() - start2
			if sut.newBranches() != set([]):
				print "ACTION:",action[0]
				for b in sut.newBranches():
					print elapsed,len(sut.allBranches()),"New branch",b
		ok = sut.safely(action)	
		if (not ok):		
			S = sut.reduce(sut.test(), lambda x: sut.fails(x) or sut.failsCheck(x))
			currTest = prettyListTest(S)				
			if currTest not in testsCovered:
				testsCovered.append(currTest)			
				print "------------------------------------------"+ "\n"			
				print "Reduced Test"
				sut.prettyPrintTest(S)
				count = count + 1
				'''print "actionsList"
				for t in prettyListTest(S):			
					print t
					print "\n" '''
				failureCount += 1
				if (FAULT_CHECK):
				    filename = "failure" + str(failureCount) + ".test"
				    sut.saveTest(S, filename)
			else:
				'''print "------------------------------------------"+ "\n"	
				print "Same test"
				sut.prettyPrintTest(S)
				break;'''
	print "Total unique tests:", count                

if (COVERAGE_REPORT):
    sut.internalReport()
