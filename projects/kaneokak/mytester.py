# The following code is based on Figure 3 in the paper, "Feedback-directed Random Test 
# Generation" by Carlos Pacheco, Shuvendu K. Lahiri, Michael D. Ernst, and Thomas Ball.

import argparse
import random
import sut
import sys
import time
from collections import defaultdict
from collections import namedtuple

fid   = 0
eseqs = []
nseqs = []
sut   = sut.sut()
rgen  = random.Random()

def parse_args():
	parser = argparse.ArgumentParser()

	parser.add_argument('-t', '--timeout', type=int, default=60, help='Timeout in seconds (default=60).')
	parser.add_argument('-s', '--seed', type=int, default=1, help='Random seed (default = 1).')
	parser.add_argument('-d', '--depth', type=int, default=None, help='Not set maximum search depth (default = None).')
	parser.add_argument('-w', '--width', type=int, default=10, help='Maximum numbers of classTable in new seq (default = 10).')
	parser.add_argument('-f', '--faults', type=int, default=0, choices=[0, 1], help='Store failure information with 1 (default = 0).')
	parser.add_argument('-c', '--coverage', type=int, default=0, choices=[0, 1], help='Produce a coverage report at the end with 1 (default = 0).')
	parser.add_argument('-r', '--running', type=int, default=0, choices=[0, 1], help='Produce a running brach coverage report with 1 (default = 0).')

	parsed_args = parser.parse_args(sys.argv[1:])

	return (parsed_args, parser)

def appendAndExecuteSeq(seq, n, eseqs, nseqs):
	global config, rgen, start

	ok = False
	propok = False
	timeover = time.time() - start >= config.timeout

	while n > 0:
		n -= 1
		a = rgen.choice(getComponent())
		seq.append(a)

		if equal(seq, eseqs) or equal(seq, nseqs):
			continue

		ok = sut.safely(a)
		propok = sut.check()

		if config.running:
			argRunning(a)

		if contract(ok, propok, seq, eseqs):
			break

		timeover = time.time() - start >= config.timeout
		if timeover:
			return (ok, propok, timeover)

	return (ok, propok, timeover)

def argFaults(fid):
	filename = 'failure' + `fid` + '.test'
	sut.saveTest(sut.test(), filename)

def argRunning(a):
	global start
	if sut.newBranches() != set([]):
		print "ACTION:", a[0]
		for b in sut.newBranches():
			print time.time() - start, len(sut.allBranches()), "New branch", b
	
def contract(ok, propok, seq, eseqs):
	global config, fid, start
	if (not ok) or (not propok):
		fid += 1

		print "***************************************************************************"
		print "FIND BUG!!", "fid:", fid, "time:", time.time() - start, "length:", len(seq)
		print "***************************************************************************"

		eseqs.append(seq)

		if config.faults:
			argFaults(fid)

def equal(seq, seqs):
	for s in seqs:
		if seq == s:
			return True
	return False

def filter(classTable):
	global config
	return max(classTable.values()) <= config.width

def getComponent():
	global rgen

	d = defaultdict(list)
	for a in sut.enabled():
		d[sut.poolUses(a[0])[0][0]].append(a)

	component = []
	for k in d.keys():
		component.append(rgen.choice(d[k]))

	return component

def getSeq():
	seq = []
	for a in getComponent():
		seq.append(a)
	return seq

def make_config(pargs, parser):
	pdict = pargs.__dict__
	key_list = pdict.keys()
	arg_list = [pdict[k] for k in key_list]
	Config = namedtuple('Config', key_list)
	nt_config = Config(*arg_list)
	return nt_config

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

def main():
	global config, rgen, start

	parsed_args, parser = parse_args()
	config = make_config(parsed_args, parser)
	print('Testing using config={}'.format(config))

	rgen.seed(config.seed)

	start = time.time()
	nseqs.append(getSeq())
	while time.time() - start < config.timeout:
		seq = rgen.choice(nseqs)[:]
		sut.replay(seq)

		if rgen.randint(0, 9) == 0:
			n = rgen.randint(2, 100)
			ok, propok, timeover = appendAndExecuteSeq(seq, n, eseqs, nseqs)
		else:
			ok, propok, timeover = appendAndExecuteSeq(seq, 1, eseqs, nseqs)

		if timeover:
			break

		if ok and propok:
			nseqs.append(seq)

	if config.coverage:
		sut.internalReport()

if __name__ == '__main__':
	main()
