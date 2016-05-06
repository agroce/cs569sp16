# The following code is based on Figure 3 in the paper, "Feedback-directed Random Test 
# Generation" by Carlos Pacheco, Shuvendu K. Lahiri, Michael D. Ernst, and Thomas Ball.

import random
import sut
import sys
import time
from collections import defaultdict

timeout = int(sys.argv[1])
seed = int(sys.argv[2])
depth = int(sys.argv[3])
width = int(sys.argv[4])
faults = int(sys.argv[5])
coverage = int(sys.argv[6])
running  = int(sys.argv[7])

def actionClassPools(sut):
	dic = defaultdict(list)
	for a in sut.actions():
		dic[sut.actionClass(a)].append(a)
	return dic

def argFaults(failureCount, sut):
	filename = 'failure' + `failureCount` + '.test'
	f = open(filename, 'w')
	f.write(str(sut.failure()))
	f.close

def argRunning(s, sut, start):
	if sut.newBranches() != set([]):
		print "ACTION:", s[0]
		for b in sut.newBranches():
			print time.time() - start, len(sut.allBranches()), "New branch", b

def initComponents(acPools, sut):
	components = []
	for k, v in acPools.iteritems():
		if not sut.dependencies(k):
			components.extend(v)
	return components

def isContracts(s, isOk, isPropOk, sut, faults, failureCount, errorSeqs):
	if (not isOk) or (not isPropOk):
		print 'FIND BUGS!!'
		if faults:
			failureCount += 1
			argFaults(failureCount, sut)
			errorSeqs.append(newSeq)
		return False
	return True

def isEnabledValue(sut):
	flag = False
	for v in sut.state()[3].itervalues():
		flag or v
	return flag

def isFilters(newSeq, numActionClasses, isOk, isPropOk, depth):
	isLessMax = max(numActionClasses.values()) <= 10
	isLessDepth = len(newSeq) <= depth
	return isLessMax and isOk and isPropOk and isLessDepth

def isNewIn(newSeq, errorSeqs, nonErrorSeqs):
	setNewSeq = set(newSeq)
	for e in errorSeqs:
		if setNewSeq < set(e):
			return True
	for n in nonErrorSeqs:
		if setNewSeq < set(n):
			return True
	return False

def printSeq(seq):
	print "printing seq..."
	for s in seq:
		print s[0]
	print ""

sut = sut.sut()
rgen = random.Random()
failureCount = 0
errorSeqs = []
nonErrorSeqs = []
start = time.time()
while time.time() - start < timeout:
	if len(sut.enabled()) < 10:
		acts = sut.randomEnableds(rgen, len(sut.enabled()))
	else:
		acts = sut.randomEnableds(rgen, 1)

	if nonErrorSeqs:
		newSeq = random.choice(nonErrorSeqs)
		newSeq.extend(acts)
	else:
		newSeq = acts

	if isNewIn(newSeq, errorSeqs, nonErrorSeqs):
		continue

	numActionClasses = dict.fromkeys(sut.actionClasses(), 0)
	for a in acts:
		numActionClasses[sut.actionClass(a)] += 1
		if running:
			argRunning(a, sut, start)
	
		isOk = sut.safely(a)
		isPropOk = sut.check()

		if not isContracts(a, isOk, isPropOk, sut, faults, failureCount, errorSeqs):
			break

	if isFilters(newSeq, numActionClasses, isOk, isPropOk, depth):
		nonErrorSeqs.append(newSeq)

	#printSeq(newSeq)

if coverage:
	sut.internalReport()
