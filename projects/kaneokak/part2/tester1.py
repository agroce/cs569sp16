# The following code is based on Figure 3 in the paper, "Feedback-directed Random Test 
# Generation" by Carlos Pacheco, Shuvendu K. Lahiri, Michael D. Ernst, and Thomas Ball.

import random
import sut
import sys
import time

def argFaults(fid):
	filename = 'failure' + `fid` + '.test'
	f = open(filename, 'w')
	f.write(str(sut.failure()))
	f.close

def argRunning(a):
	if sut.newBranches() != set([]):
		print "ACTION:", a[0]
		for b in sut.newBranches():
			print time.time() - start, len(sut.allBranches()), "New branch", b
	
def contracts(seq, errorseqs, ok, propok):
	if (not ok) or (not propok):
		print 'FIND BUGS!!'
		if faults:
			fid += 1
			argFaults(fid)
			errorseqs.append(seq)
		return True
	return False

def filters(seq, classTable, ok, propok):
	notmany = max(classTable.values()) <= width
	lessdepth = len(seq) <= depth
	return (ok and propok and lessdepth and notmany)

def oldseq(seq, seqs):
	setSeq = set(seq)
	for s in seqs:
		if setSeq <= set(s):
			return True
	return False

def printSeq(seq):
	print "printing seq..."
	for a in seq:
		print a[0]
	print ""

def printSeqs(seqs):
	print "printing seqs..."
	for seq in seqs:
		for a in seq:
			print a[0]
		print ""

timeout = int(sys.argv[1])
seed = int(sys.argv[2])
depth = int(sys.argv[3])
width = int(sys.argv[4])
faults = int(sys.argv[5])
coverage = int(sys.argv[6])
running  = int(sys.argv[7])

sut = sut.sut()
rgen = random.Random()
rgen.seed(seed)
fid = 0
errorseqs = []
nonerrorseqs = [[]]

start = time.time()
while time.time() - start < timeout:
	sut.restart()
	seq = rgen.choice(nonerrorseqs)[:]
	classTable = dict.fromkeys(sut.actionClasses(), 0)
	for a in seq:
		a[2]()
		classTable[sut.actionClass(a)] += 1

	if rgen.randint(0, 9) == 0:
		n = rgen.randint(2, 100)
		while n > 0:
			n -= 1
			a = sut.randomEnabled(rgen)	
			seq.append(a)
			if oldseq(seq, errorseqs) or oldseq(seq, nonerrorseqs):
				continue
			ok = sut.safely(a)
			propok = sut.check()
			if running:
				argRunning(a)
			if contracts(seq, errorseqs, ok, propok):
				break
			classTable[sut.actionClass(a)] += 1
	else:
		a = sut.randomEnabled(rgen)	
		seq.append(a)
		if oldseq(seq, errorseqs) or oldseq(seq, nonerrorseqs):
			continue
		ok = sut.safely(a)
		propok = sut.check()
		if running:
			argRunning(a)
		if contracts(seq, errorseqs, ok, propok):
			break
		classTable[sut.actionClass(a)] += 1

	if filters(seq, classTable, ok, propok):
		nonerrorseqs.append(seq)

if coverage:
	sut.internalReport()
