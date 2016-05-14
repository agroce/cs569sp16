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
	
def contracts(seq, eseqs, ok, propok):
	global fid
	if (not ok) or (not propok):
		print 'FIND BUGS!!'
		if faults:
			fid += 1
			argFaults(fid)
			eseqs.append(seq)
		return True
	return False

def equal(seq, seqs):
	for s in seqs:
		if seq == s:
			return True
	return False

def genAndExeSeq(n, seq, eseqs, nseqs):
	ok = False
	propok = False
	classTable = dict.fromkeys(sut.actionClasses(), 0)
	timeover = False
	while n > 0:
		n -= 1
		a = sut.randomEnabled(rgen)	
		seq.append(a)
		if equal(seq, eseqs) or equal(seq, nseqs):
			continue
		ok = sut.safely(a)
		propok = sut.check()
		if running:
			argRunning(a)
		if contracts(seq, eseqs, ok, propok):
			break
		classTable[sut.actionClass(a)] += 1
		timeover = time.time() - start >= timeout
		if timeover:
			return (ok, propok, classTable, timeover)
	return (ok, propok, classTable, timeover)

def filters(seq, ok, propok, classTable):
	lessdepth = len(seq) <= depth
	notmany   = max(classTable.values()) <= width
	return (ok and propok and lessdepth and notmany)

def printClassTable(classTable):
	print "printing classTable..."
	for k, v in classTable.iteritems():
		print k, v
	print ""

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

start = time.time()
while time.time() - start < timeout:
	seq = rgen.choice(nseqs)[:]
	sut.replay(seq)

	if rgen.randint(0, 9) == 0:
		n = rgen.randint(2, 100)
		ok, propok, classTable, timeover = genAndExeSeq(n, seq, eseqs, nseqs)
		if timeover:
			break
	else:
		ok, propok, classTable, timeover = genAndExeSeq(1, seq, eseqs, nseqs)
		if timeover:
			break

	if filters(seq, ok, propok, classTable):
		nseqs.append(seq)

if coverage:
	sut.internalReport()
