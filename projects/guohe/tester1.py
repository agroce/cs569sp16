import sut
import random
import sys
import time

rgen = random.Random()
depth = 50

explore = 0.7

savecoverage_test = None

Number = 0

sut = sut.sut()

BUDGET = int(sys.argv[1])
seed = int(sys.argv[2])
depth = int(sys.argv[3])
width = int(sys.argv[4])
faults = int(sys.argv[5])
coverage = int(sys.argv[6])
running = int(sys.argv[7])

bugs_found = 0

Cover_percent = {}
Coverage_W = []
Least = None
weight = 0
Coverage_all = 100
# coverage tolerance
start = time.time()
def avlfunction():
	global storedTest,sortedCov,savecoverage_test,rgen,depth,explore,savecoverage_test,Number,sut,BUDGET,seed,width,faults,coverage,running,bugs_found,Cover_percent,Coverage_W,Least,weight,Coverage_all,start
	for s in xrange(0,depth):
		act = sut.randomEnabled(rgen)
		ok = sut.safely(act)
		if running:
			if len(sut.newBranches()) > 0:
				print "ACTION:", act[0]
				for d in sut.newBranches():
					print time.time() - start, len(sut.allBranches()),"New branch",d 	
		if len(sut.newStatements()) > 0:
				savecoverage_test = sut.state()
				storedTest = True
				print "New state",sut.newStatements()
		#if len(sut.newStatements()) > 0:
		#	savecoverage_test = sut.state()
		#	storedTest = True
		#	print "New state",sut.newStatements()
		if (not storedTest) and (Least != None) and (Least in sut.currStatements()):
			#print "SAW LEAST COVERED STATEMENT, STORING TEST"
			savecoverage_test = sut.state()
			storedTest = True
		Number += 1
		if faults:
			if not ok:
				bugs_found += 1
				print "FAILURE"
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


def newFunction():
	global storedTest,savecoverage_test,start,BUDGET,rgen,depth,explore,savecoverage_test,Number,sut,BUDGET,seed,width,faults,coverage,running,bugs_found,Cover_percent,Coverage_W,Least,weight,Coverage_all,start
	sut.restart()
	if (savecoverage_test != None) and (rgen.random() > explore):
		print "processing"
		sut.backtrack(savecoverage_test)
	storedTest = False
	print "part1: test the AVL tree"
	avlfunction()
	print "part2: processing the coverage"
	
	for t in sortedCov:
		weight = (Coverage_all - Cover_percent[t])
		#weightedCov = t*weight
		#if weightedCov < 20:
		if time.time() - start > BUDGET:
			return
		if weight > 80:
			Coverage_W.append(t)
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