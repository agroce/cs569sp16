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


def RandomSeqs(nonErrSeqs, n = 1):
	if (nonErrSeqs == [] or n > len(nonErrSeqs)):
		return []

	r = [random.choice(nonErrSeqs) for i in xrange(n)]
	return r

def ExecutingInfo(run, elapsed):
	if sut.newBranches() != set([]):
		print "ACTION:", run[0]
		for b in sut.newBranches():
			print "Runtime:", elapsed, "||", "branch Count:", len(sut.allBranches())
			print "New branch:", b
			print "========================================================================================"

def RecordFail():
	BUG = 0
	while os.path.exists('failure' + str(BUG) + 'test') == True:
		BUG += 1

	records = open('failure' + str(BUG) + '.test', 'w')
	records.write(str(sut.failure()))
	records.close

def main():
	non_Errtemp = []
	Errtemp = []
	rgen = random.Random()
	rgen.seed(seed)
	sTime = time.time()
	Num_BUG = 0
	Action_Count = 0

	while (time.time() - sTime) < timeout:
		newSeqs = sut.randomEnableds(rgen, depth)
		Seqs = RandomSeqs(non_Errtemp, n = 5)
		newSeqs.extend(Seqs)
		
		not_okay = False
		for run in newSeqs:
			if running == 1:
				ExecutingInfo(run, elapsed = (time.time() - sTime))

			okay = sut.safely(run)
			if sut.check() == False:
				not_okay = True

			Action_Count += 1

			if faults == 1:
				if okay == False or not_okay == True:
					RecordFail()
					Num_BUG += 1
					print "BUG FOUND!"
					print sut.failure()
					print "REDUCING ..."
					R = sut.reduce(sut.test(), sut.fails, True, True)
					sut.prettyPrintTest(R)
					print sut.failure()
					filename = 'failure%d.test' % Num_BUG
					sut.saveTest(R , filename)
					break

		if not_okay == True:
			Errtemp += newSeqs
		else:
			non_Errtemp += newSeqs

	print Num_BUG, "BUGS FOUND!"
	print "Total Actions: ", Action_Count
	print "Total Runtime: ", (time.time() - sTime)


if __name__ == '__main__':

	main()

	print ""

	if coverage == 1:
		sut.internalReport()

