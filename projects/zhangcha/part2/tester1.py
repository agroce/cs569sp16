import sut
import sys
import random
import time
import math
import os
import traceback
import argparse


TIMEOUT = int(sys.argv[1])

SEED = int(sys.argv[2])

DEPTH = int(sys.argv[3])

WIDTH = int(sys.argv[4])

FAULTS = int(sys.argv[5])

COVERAGE = int(sys.argv[6])

RUNNING = int(sys.argv[7])

sut=sut.sut()
sut.silenceCoverage()
rgen = random.Random()

coverageCount = {}

actCount = 0
bugs = 0

visited = []
failPool = []
belowMid = set([])

def randomAction():
	global actCount, bugs, failPool
	act = sut.randomEnabled(rgen)
	actCount += 1
	ok = sut.safely(act)
	if not ok:
		failures()
	else:
		Statement()
	return ok  

def Statement():
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


queue =[sut.state()]

#########1
print "1"
start1 = time.time()
print "Testing of first", TIMEOUT/2, "time..."
while time.time() - start1 < TIMEOUT/2:
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
for s in sortedCov:
	print s, coverageCount[s]   

print "2"
start2 = time.time()
print "Testing of second", TIMEOUT/2, "time..."
while time.time() - start2 < TIMEOUT/2:
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
	print s, coverageCount[s]

print bugs,"FAILED"
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-start
