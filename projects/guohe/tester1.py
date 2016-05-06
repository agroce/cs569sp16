import sut
import random
import sys
import time

rgen = random.Random()
depth = 100

explore = 0.7

savecoverage_test = None

Number = 0

sut = sut.sut()

BUDGET = int(sys.argv[1])
seed = int(sys.argv[2])
width = int(sys.argv[3])
faults = int(sys.argv[4])
coverage = int(sys.argv[5])
running = int(sys.argv[6])

bugs_found = 0

Cover_percent = {}
Coverage_W = []
Least = None
weight = 0
Coverage_all = 100
# coverage tolerance



start = time.time()
def newFunction():
	global savecoverage_test,rgen,depth,explore,savecoverage_test,Number,sut,BUDGET,seed,width,faults,coverage,running,bugs_found,Cover_percent,Coverage_W,Least,weight,Coverage_all,start
	sut.restart()
	if (savecoverage_test != None) and (rgen.random() > explore):
		print "processing"
		sut.backtrack(savecoverage_test)
	storedTest = False
	print "part1: AVL"
	for s in xrange(0,100):
		act = sut.randomEnabled(rgen)
		ok = sut.safely(act)
		if len(sut.newStatements()) > 0:
			savecoverage_test = sut.state()
			storedTest = True
			print "New state",sut.newStatements()
		if (not storedTest) and (Least != None) and (Least in sut.currStatements()):
			#print "SAW LEAST COVERED STATEMENT, STORING TEST"
			savecoverage_test = sut.state()
			storedTest = True
		Number += 1
		if not ok:
			bugs_found += 1
			print "FAILURE"
            #sut.prettyPrintTest(sut.test())
			print sut.failure()
			R = sut.reduce(sut.test(),sut.fails, True, True)
			sut.prettyPrintTest(R)
			print sut.failure()
			break
	for s in sut.currStatements():
		if s not in Cover_percent:
			Cover_percent[s] = 0
		Cover_percent[s] += 1
	sortedCov = sorted(Cover_percent.keys(), key=lambda x: Cover_percent[x])
	# go through the sortedCov and assign weights on them
	print "part2: coverage"
	# weight is calculated by: coverage * (mean - Cover_percent),
	# the greater the difference between the mean and the coverage count,
	# the larger your weight will be
	for t in sortedCov:
		weight = (Coverage_all - Cover_percent[t])
		weightedCov = t*weight
		if weightedCov > 20:
			Coverage_W.append(weightedCov)
			print "Coverage:", t

def main():
	global start,BUDGET,sortedCov,Cover_percent,Number
	while time.time()-start < BUDGET:
		newFunction()
	sut.internalReport()
	sortedCov = sorted(Cover_percent.keys(), key=lambda x: Cover_percent[x])

	for s in sortedCov:
		print s, Cover_percent[s]
	print bugs_found,"FAILED"
	print "ACTIONS_total",Number
	print "RUNTIME_total",time.time()-start
if __name__ == '__main__':
	main()