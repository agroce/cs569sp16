

import random
import sut
import sys
import time
import os


timeout  = int(sys.argv[1])
seed     = int(sys.argv[2])
depth    = int(sys.argv[3])
width    = int(sys.argv[4])
faults   = int(sys.argv[5])
coverage = int(sys.argv[6])
running  = int(sys.argv[7])

ErrSeqs    = []
nonErrSeqs = []
sut        = sut.sut()

def DropDups(newSeqs):
	for n in nonErrSeqs:
		if set(newSeqs) < set(n):
			return True

	for e in ErrSeqs:
		if set(newSeqs) < set(e):
			return True

	return False

def RandomSsVs(nonErrSeqs, n = 1):
	if (nonErrSeqs == [] or n > len(nonErrSeqs)):
		return []
	return [random.choice(nonErrSeqs) for i in xrange(n)]

def SetFlags(newSeqs):
	pass

def RunningInfo(run, elapsed):
	if sut.newBranches() != set([]):
		print "ACTION: ", run[0]
		for b in sut.newBranches():
			print elapsed, len(sut.allBranches()), "New Branch", b

def RecordFail():
	count = 0
	while os.path.exists('failure' + str(count) + 'test') == True:
		count = count + 1

	records = open('failure' + str(count) + '.test', 'w')
	records.write(str(sut.failure()))
	records.close

def Operation():
	rgen = random.Random()
	rgen.seed(seed)
	non_Errtemp = []
	Errtemp = []

	sTime = time.time()
	while (time.time() - sTime) < timeout:
		newSeqs = sut.randomEnableds(rgen, depth)
		Seqs = RandomSsVs(non_Errtemp, n = 7)
		newSeqs.extend(Seqs)

		if DropDups(newSeqs):
			continue

		not_okay = False
		for run in newSeqs:
			if running == 1:
				RunningInfo(run, elapsed = (time.time() - sTime))

			okay = sut.safely(run)
			if sut.check() == False:
				not_okay = True

			if faults == 1:
				if okay == False or not_okay == True:
					RecordFail()
					print "BUG FOUND!"
					return non_Errtemp, Errtemp

		if not_okay == True:
			Errtemp += newSeqs
		else:
			non_Errtemp += newSeqs
			SetFlags(newSeqs)

	return non_Errtemp, Errtemp

def Report():
	if coverage == 1:
		sut.internalReport()

if __name__ == '__main__':

	Operation()

	Report()

