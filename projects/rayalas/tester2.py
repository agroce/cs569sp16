import sut
import random
import sys
import time

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

TIME_BUDGET = int(sys.argv[1])

SEED = int(sys.argv[2])

DEPTH = int(sys.argv[3])

WIDTH = int(sys.argv[4])

FAULT_CHECK = int(sys.argv[5])

COVERAGE_REPORT = int(sys.argv[6])

RUNNING_DETAIL = int(sys.argv[7])

rgen = random.Random()
rgen.seed(SEED)
count = 0
sut = sut.sut()
#sut.silenceCoverage()

start = time.time()
while time.time()-start < TIME_BUDGET:
    sut.restart()
    for s in xrange(0,DEPTH):
	action = sut.randomEnabled(rgen)
	if(RUNNING_DETAIL):	
        	elapsed = time.time() - start
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
