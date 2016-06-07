# The following code is based on Figure 3 in the paper, "Feedback-directed Random Test 
# Generation" by Carlos Pacheco, Shuvendu K. Lahiri, Michael D. Ernst, and Thomas Ball.

import random
import sut
import sys
import time

timeout  = int(sys.argv[1])
seed     = int(sys.argv[2])
depth    = int(sys.argv[3])
width    = int(sys.argv[4])
faults   = int(sys.argv[5])
coverage = int(sys.argv[6])
running  = int(sys.argv[7])

fid   = 0
eseqs = []
nseqs = [[]]
sut   = sut.sut()
rgen  = random.Random()
rgen.seed(seed)

def appendAndExecuteSeq(seq, n, eseqs, nseqs):
	ok = False
	propok = False
	classTable = dict.fromkeys(sut.actionClasses(), 0)
	timeover = time.time() - start >= timeout

	while n > 0:
		n -= 1
		a = sut.randomEnabled(rgen)
		seq.append(a)

		if equal(seq, eseqs) or equal(seq, nseqs):
			continue

		ok = sut.safely(a)
		propok = sut.check()
		classTable[sut.actionClass(a)] += 1

		if running:
			argRunning(a)

		if contract(ok, propok, seq, eseqs):
			break

		timeover = time.time() - start >= timeout
		if timeover:
			return (ok, propok, classTable, timeover)

	return (ok, propok, classTable, timeover)

def argFaults(fid):
	filename = 'failure' + `fid` + '.test'
	sut.saveTest(sut.test(), filename)

def argRunning(a):
	if sut.newBranches() != set([]):
		print "ACTION:", a[0]
		for b in sut.newBranches():
			print time.time() - start, len(sut.allBranches()), "New branch", b
	
def contract(ok, propok, seq, eseqs):
	global fid
	if (not ok) or (not propok):
		fid += 1

		print "***************************************************************************"
		print "FIND BUG!!", "fid:", fid, "time:", time.time() - start, "length:", len(seq)
		print "***************************************************************************"

		eseqs.append(seq)

		if faults:
			argFaults(fid)

def equal(seq, seqs):
	for s in seqs:
		if seq == s:
			return True
	return False

def filter(classTable):
	return max(classTable.values()) <= width

def printSeq(seq):
	print "len:", len(seq)
	for a in seq:
		print a[0]
	print ""

def printSeqs(seqs):
	sortedSeqs = sorted(seqs, key = lambda x: len(x))
	for seq in sortedSeqs:
		print "len:", len(seq)
		for a in seq:
			print a[0]
		print ""

start = time.time()
while time.time() - start < timeout:
	seq = rgen.choice(nseqs)[:]
	sut.replay(seq)

	if rgen.randint(0, 9) == 0:
		n = rgen.randint(2, 100)
		ok, propok, classTable, timeover = appendAndExecuteSeq(seq, n, eseqs, nseqs)
	else:
		ok, propok, classTable, timeover = appendAndExecuteSeq(seq, 1, eseqs, nseqs)

	if timeover:
		break

	if ok and propok and filter(classTable):
		nseqs.append(seq)

if coverage:
	sut.internalReport()
