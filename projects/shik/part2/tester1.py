import sut
import sys
import random
import time
import math
import os

start = time.time()

TIMEOUT = int(sys.argv[1])

SEED = int(sys.argv[2])

DEPTH = int(sys.argv[3])

WIDTH = int(sys.argv[4])

FAULTS = int(sys.argv[5])

COVERAGE = int(sys.argv[6])

RUNNING = int(sys.argv[7])

sut=sut.sut()
#sut.silenceCoverage()
rgen = random.Random()

coverageCount = {}

actCount = 0
bugs = 0
visited = []
failPool = []
belowMid = set([])

def failures():
	global bugs,coverageCount
	bugs += 1
	print "FOUND A FAILURE"
	print sut.failure()
	print "REDUCING"
	failPool.append(sut.test())
	for s in sut.currStatements():
		if s not in coverageCount:
			coverageCount[s] = 0
		coverageCount[s] += 1  
	print sut.failure()
	if FAULTS:
		with open("failure"+str(bugs)+".test",'w') as f:
			f.write('\n'+str(bugs)+' bugs found:\n')
			f.write(str(sut.failure())+'\n')
		

	sut.restart()

def randomAction():
	global actCount, failPool
	act = sut.randomEnabled(rgen)
	actCount += 1
	ok = sut.safely(act)
	elapsed = time.time() - start
	if RUNNING:
		if sut.newBranches() != set([]):
			print "ACTION:",act[0]
			for d in sut.newBranches():
				print elapsed,len(sut.allBranches()),"New branch",d
			sawNew = True
		else:
			sawNew = False

		if sut.newStatements() != set([]):
			print "ACTION:",act[0]
			for s in sut.newStatements():
				print elapsed,len(sut.allStatements()),"New statement",s
			sawNew = True
		else:
			sawNew = False

	if not ok:
		failures()
	else:
		newStatement()
	return ok  

def newStatement():
	global belowMid,lastAddCoverage 
	if len(sut.newStatements()) != 0:
		oldTest = list(sut.test())
		storeTest = sut.reduce(oldTest,sut.coversStatements(sut.newStatements()))
		sut.replay(oldTest)
		visited.append((storeTest, set(sut.currStatements())))
		lastAddCoverage = set(sut.currStatements())
		return
	for s in belowMid:
		if s in sut.currStatements() and s not in lastAddCoverage:
			visited.append((list(sut.test()), set(sut.currStatements())))
			lastAddCoverage = set(sut.currStatements())
			return

def findMid():
	global belowMid

	belowMid = set([])
	sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])
	ss = len(sortedCov)/2
	for s in sortedCov:
		if coverageCount[s]< coverageCount[sortedCov[ss]]:
			belowMid.add(s)
		else:
			break
	#print len(belowMid),"STATEMENTS BELOW MID COVERAGE OUT OF",len(coverageCount)
	
		


queue =[sut.state()]

#########1
print "STARTING FIRST HALF TIME"
print "Testing of half", TIMEOUT*0.5, "time..."
while time.time() - start < TIMEOUT/2.:
	sut.restart()
	for s in xrange (0,DEPTH):
		if not randomAction():
			break
	for s in sut.currStatements():
		if s not in coverageCount:
			coverageCount[s] = 0
		coverageCount[s] += 1 

sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])
ss = len(coverageCount)/2
coverMid = coverageCount[sortedCov[ss]]
print "MID COVERAGE IS",coverMid
for s in sortedCov:
	print s, coverageCount[s]   

#########

#########2
print "STARTING REST HALF TIME"
while time.time() - start < TIMEOUT:
	findMid()
	queue = []
	for (t,c) in visited:
		for s in c:
			if s in belowMid:
				queue.append((t,c))
				break

	lastAddCoverage = set([])
	sut.restart()
	if rgen.random() > 0.7:
		sut.replay(rgen.choice(queue)[0])
		lastAddCoverage = set(sut.currStatements())  
	for d in xrange (0,DEPTH):
		if not randomAction():
			break
	for s in sut.currStatements():
		if s not in coverageCount:
			coverageCount[s] = 0
		coverageCount[s] += 1 
print "\nBelowMid coverageCount 2nd running Coverage results: "

sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])
ss = len(coverageCount)/2
coverMid = coverageCount[sortedCov[ss]]
print "MID COVERAGE IS",coverMid
for s in sortedCov:
	print s, coverageCount[s]
print "\nBelowMid coverageCount 2nd running Coverage results has printed\n"


if COVERAGE:
	sut.internalReport()

print bugs,"FAILED"
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-start
