import sut
import random
import sys
import time
import math

TIME_BUDGET = int(sys.argv[1])

SEED = int(sys.argv[2])

DEPTH = int(sys.argv[3])

#WIDTH = int(sys.argv[4])

#FAULT_CHECK = int(sys.argv[5])

#COVERAGE_REPORT = int(sys.argv[6])

#RUNNING_DETAIL = int(sys.argv[7])

rgen = random.Random()
rgen.seed(SEED)


sut = sut.sut()
sut.restart()

visited = []
S = []
S.append((sut.state(),[]))
test = []
coverageCount = {}

time_start = time.time()


d = 1
bugs = 0
while d<=DEPTH:
	elipse = time.time() - time_start
	if elipse>=TIME_BUDGET:
		break
	
	else:
		print "DEPTH",d,"QUEUE SIZE",len(S)
	d+=1

	while S != []:
		(v, test) = S.pop()
		sut.backtrack(v)
		if (v not in visited) and (len(test) < DEPTH):
			visited.append(v)
			trans = sut.enabled()
			rgen.shuffle(trans)
			for (name, guard, act) in trans:
				test.append(name)
				action = sut.randomEnabled(rgen)
				ok = sut.safely(action)
				propok = sut.check()
				if ((not ok) or (not propok)):
					sut.prettyPrintTest(sut.test())
					print "TEST FAILED"
					print "REDUCING..."
					R = sut.reduce(sut.test(), lambda x: sut.fails(x) or sut.failsCheck(x))
					sut.prettyPrintTest(R)
					print "NORMALIZING..."
					N = sut.normalize(R, lambda x: sut.fails(x) or sut.failsCheck(x))
					sut.prettyPrintTest(N)
					sut.generalize(N, lambda x: sut.fails(x) or sut.failsCheck(x))
					sys.exit(1)
				S.append((sut.state(), test))
print bugs
if (COVERAGE_REPORT):
    sut.internalReport()

