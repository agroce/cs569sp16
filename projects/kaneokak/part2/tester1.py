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

#timeout = 30
#seed = 1
#depth = 100
#width = 1
#faults = 1
#coverage = 1
#running = 1

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

def isNotContracts(newSeq, ok, propok, sut, faults, failureCount, errorSeqs):
	if (not ok) or (not propok):
		print 'FIND BUGS!!'
		if faults:
			failureCount += 1
			argFaults(failureCount, sut)
			errorSeqs.append(newSeq)
		return True
	return False

def isEnabledValue(sut):
	flag = False
	for v in sut.state()[3].itervalues():
		flag or v
	return flag

def isFilters(newSeq, actionClassesCounts, depth, ok, propok):
	isLessMax = max(actionClassesCounts.values()) <= 10
	isLessDepth = len(newSeq) <= depth
	return (ok and propok and isLessDepth and isLessMax)

def isNotNewSeq(seq, seqs):
	setSeq = set(seq)
	for s in seqs:
		if setSeq <= set(s):
			return True
	return False

def isSeqsEqual(seqs):
	flag = False
	pre = set()
	for l in seqs:
		cur = set(l)
		flag = cur == pre
		pre = cur
	return flag

def printSeq(seq):
	print "printing seq..."
	for s in seq:
		print s[0]
	print ""

def printSeqs(seqs):
	print "printing seqs..."
	for l in seqs:
		for s in l:
			print s[0]
		print ""

sut = sut.sut()
rgen = random.Random()
rgen.seed(seed)
failureCount = 0
errorSeqs = []
nonErrorSeqs = [[]]
start = time.time()
while time.time() - start < timeout:
	sut.restart()
	newSeq = rgen.choice(nonErrorSeqs)[:]
	actionClassesCounts = dict.fromkeys(sut.actionClasses(), 0)
	for s in newSeq:
		s[2]()
		actionClassesCounts[sut.actionClass(s)] += 1

	if rgen.randint(0, 9) == 0:
		n = rgen.randint(2, 100)
		while n > 0:
			n -= 1
			a = sut.randomEnabled(rgen)	
			newSeq.append(a)
			if isNotNewSeq(newSeq, errorSeqs) or isNotNewSeq(newSeq, nonErrorSeqs):
				continue
			if running:
				argRunning(a, sut, start)
			ok = sut.safely(a)
			propok = sut.check()
			if isNotContracts(newSeq, ok, propok, sut, faults, failureCount, errorSeqs):
				break
			actionClassesCounts[sut.actionClass(a)] += 1
	else:
		a = sut.randomEnabled(rgen)	
		newSeq.append(a)
		if isNotNewSeq(newSeq, errorSeqs) or isNotNewSeq(newSeq, nonErrorSeqs):
			continue
		if running:
			argRunning(a, sut, start)
		ok = sut.safely(a)
		propok = sut.check()
		if isNotContracts(newSeq, ok, propok, sut, faults, failureCount, errorSeqs):
			break
		actionClassesCounts[sut.actionClass(a)] += 1

	if isFilters(newSeq, actionClassesCounts, depth, ok, propok):
		nonErrorSeqs.append(newSeq)

	#printSeq(newSeq)
	#printSeqs(nonErrorSeqs)

if coverage:
	sut.internalReport()
