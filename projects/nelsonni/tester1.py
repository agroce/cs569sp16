#!/usr/bin/python

import sut
import random
import sys
import time
import math
from optparse import OptionParser

def main(argv):
	global sut, rgen, coverageMap, randomPool, failedPool

	parse_options(argv)

	# GLOBAL VARIABLES
	sut = sut.sut()
	rgen = random.Random(options.seed)
	coverageMap    = {}
	randomPool     = []
	restrictedPool = []
	failedPool     = []

	# BEGIN TEST GENERATION
	total_start = time.time()
	
	print "STARTING PHASE 1"
	phase1()
	print "TESTS:",len(randomPool)
	print "BUGS:",len(failedPool)

	print "================================="
	print "STARTING PHASE 2"
	phase2()
	print "TESTS:",len(randomPool)
	print "BUGS:",len(failedPool)

	print "================================="
	print "TOTAL ELAPSED:",(time.time() - total_start)
	print "TOTAL TESTS:",len(randomPool)
	print "TOTAL BUGS:",len(failedPool)

	if (options.coverage):
		sut.internalReport()


def randomAction():
	act = sut.randomEnabled(rgen)
	ok = sut.safely(act)
	if ok:
		expandPool()
		if (options.running):
			runtimeCoverage(act)
	else:
		print "FOUND A FAILURE"
		print sut.failure()
		failedPool.append(sut.test())
		collectCoverage()

		print "REDUCING FAILURE"
		R = sut.reduce(sut.test(),sut.fails, True, True)
		sut.prettyPrintTest(R)
		print sut.failure()

		sut.restart()
	return ok




def phase1():
	BUDGET = (options.width/float(100)*options.timeout)
	DEPTH = options.depth
	print "BUDGET:",BUDGET,"seconds","DEPTH:",DEPTH,"tests"

	start = time.time()
	while time.time()-start < BUDGET:
		sut.restart()
		for s in xrange(0,DEPTH):
			if not randomAction():
				break
		collectCoverage()

def phase2():
	global coverageMap
	BUDGET = options.timeout - (options.width/float(100)*options.timeout) 
	print "BUDGET:",BUDGET,"seconds"
	print "WIDTH:",options.width,"shared ancestor actions"

	start = time.time()
	while time.time()-start < BUDGET:
		restrictPool()

	#printCoverage()

def collectCoverage():
	global coverageMap
	for s in sut.currStatements():
		if s not in coverageMap:
			coverageMap[s] = 0
		coverageMap[s] += 1

def printCoverage():
	global coverageMap
	sortedMap = sorted(coverageMap.keys(), key=lambda x: coverageMap[x], reverse=True)
	t = threshold()
	print "THRESHOLD COVERAGE:",t,"statements"
	for s in sortedMap:
		if coverageMap[s] < t:
			print s, coverageMap[s]

def expandPool():
	if len(sut.newStatements()) != 0:
		test = sut.reduce(sut.test(),sut.coversStatements(sut.newStatements()))
		state = sut.state()
		sut.backtrack(state)
		randomPool.append((test, set(sut.currStatements())))
		return
	thresholdSet = belowThreshold()
	for s in thresholdSet:
		if s in sut.currStatements():
			randomPool.append((list(sut.test()), set(sut.currStatements())))
			return

def restrictPool():
	global restrictedPool
	restrictedPool = []
	thresholdSet = belowThreshold()
	print "thresholdSet:",len(thresholdSet)
	for (t,c) in randomPool:
		for s in c:
			if s in thresholdSet:
				restrictedPool.append((t,c))
				break
	print "RANDOM POOL:",len(randomPool),"RESTRICTED POOL:",len(restrictedPool)

def belowThreshold():
	global coverageMap
	thresholdSet = set([])
	sortedMap = sorted(coverageMap.keys(), key=lambda x: coverageMap[x], reverse=True)
	limit = threshold()
	for s in sortedMap:
		if coverageMap[s] < limit:
			thresholdSet.add(s)
		else:
			break
	print "belowThreshold: found",len(thresholdSet)
	return thresholdSet

def threshold():
	global coverageMap
	sortedMap = sorted(coverageMap.keys(), key=lambda x: coverageMap[x], reverse=True)
	sortedCov = map(lambda x:(x[1]),sortedMap)
	return percentile(sortedCov, 0.1)

def runtimeCoverage(action):
	elapsed = time.time() - start

	if sut.newBranches() != set([]):
		print "ACTION:", action[0]
		for b in sut.newBranches():
			print elapsed, len(sut.allBranches()),"New branch", b

	if sut.newStatements() != set([]):
		print "ACTION:",action[0]
		for s in sut.newStatements():
			print elapsed, len(sut.newStatements()), "New statement", s

def percentile(N, percent, key=lambda x:x):
    """
    Find the percentile of a list of values.
    source: http://code.activestate.com/recipes/511478/

    @parameter N - is a list of values. Note N MUST BE already sorted.
    @parameter percent - a float value from 0.0 to 1.0.
    @parameter key - optional key function to compute value from each element of N.

    @return - the percentile of the values
    """
    if not N:
        return None
    k = (len(N)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(N[int(k)])
    d0 = key(N[int(f)]) * (c-k)
    d1 = key(N[int(c)]) * (k-f)
    return d0+d1

def parse_options(argv):
	global options 
	parser = OptionParser()
	parser.add_option('-t', '--timeout', action="store", type="int", dest="timeout", default=30, help="time in seconds for testing")
	parser.add_option('-s', '--seed', action="store", type="int", dest="seed", default=10, help="seed used for random number generation")
	parser.add_option('-d', '--depth', action="store", type="int", dest="depth", default=10, help="maximum length of a test")
	parser.add_option('-p', '--percent', action="store", type="int", dest="percent", default=50, help="percent (0-100%) of timeout spent exploring in PHASE 1")
	parser.add_option('-w', '--width', action="store", type="int", dest="width", default=50, help="minimum shared ancestory for grouping in PHASE 2")
	parser.add_option('-f', '--fault', action="store_true", dest="fault", default=False, help="check for faults in the SUT")
	parser.add_option('-c', '--coverage', action="store_true", dest="coverage", default=False, help="produce a final coverage report")
	parser.add_option('-r', '--running', action="store_true", dest="running", default=False, help="produce running info on branch coverage")
	options, args = parser.parse_args()
	if (options.percent < 0 or options.percent > 100):
		print "Error! Option out of bounds: percent (-p) option must be a value between 0 and 100."
		sys.exit(1)

if __name__ == "__main__":
	main(sys.argv[1:])