import os
import sys
import sut
import random
import time
import string
import argparse
from collections import namedtuple

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('-t', '--timeout', type = int, default = 300, help = 'Timeout in seconds (300 default).')
	parser.add_argument('-s', '--seed', type = int, default = None, help = 'Random seed (default = None).')
	parser.add_argument('-d', '--depth', type = int, default = 10, help = 'Maximum search depth (10 default).')
	parser.add_argument('-w', '--width', type = int, default = 10, help = 'Maximum search width (10 default).')
	parser.add_argument('-f', '--faults', type = int, default = 0, help = 'Faults display (default = 0).')
	parser.add_argument('-c', '--coverage', type = int, default = 0, help = 'Coverage display (default = 0).')
	parser.add_argument('-r', '--running', type = int, default = 0, help = 'Running display (default = 0).')
	parser.add_argument('-p', '--check', type = int, default = 0, help = 'Checking property (default = 0).')
	parser.add_argument('-sc', '--silence', type = int, default = 0, help = 'Coverage silence (default = 0).')
	parser.add_argument('-cd', '--coverdetail', type = int, default = 0, help = 'Display collected coverage in detail (default = 0).')
	parser.add_argument('-rd', '--resultdetail', type = int, default = 0, help = 'Display result in detail (default = 0).')
	parsed_args = parser.parse_args(sys.argv[1:])
	return (parsed_args, parser)

def make_config(parsed_args, parser):
	pdict = parsed_args.__dict__
	key_list = pdict.keys()
	arg_list = [pdict[k] for k in key_list]
	Config = namedtuple('Config', key_list)
	nt_config = Config(*arg_list)
	return nt_config

def collectCoverage():
    global branchCount, statementCount
    for s in sut.currBranches():
    	if s not in branchCount:
    		branchCount[s] = 1
    	else:
    		branchCount[s] += 1

    for s in sut.currStatements():
        if s not in statementCount:
            statementCount[s] = 1
        else:
        	statementCount[s] += 1

def printCoverage():
	sortedBran = sorted(branchCount.keys(), key = lambda x : branchCount[x]) 
	branSum = sum(branchCount.values())
	branMean = branSum / (1.0*len(branchCount))
	print "Mean Branches is", branMean
	for s in sortedBran:
		print s, branchCount[s]

	sortedStat = sorted(statementCount.keys(), key = lambda x : statementCount[x])
	stateSum = sum(statementCount.values())
	stateMean = stateSum / (1.0*len(statementCount))
	print "Mean statements is", stateMean
	for s in sortedStat:
		print s, statementCount[s]

def failure():
	global bugs
	bugs += 1
	collectCoverage()
	R = sut.reduce(sut.test(), sut.fails, True, True)
	if config.faults :
		filename = 'failure%d.test'%bugs
		sut.saveTest(sut.test(), filename)
	sut.prettyPrintTest(R)
	sut.restart()
	return

def savingTest():
	global sut, fullPool, savedTest, savedFlag
	if len(sut.newBranches()) > 0:
		savedTest = sut.state()
		savedFlag = True
	if len(sut.newStatements()) > 0:
		savedTest = sut.state()
		savedFlag = True
	return

def randomAct():
	global sut, actCount, R
	act = sut.randomEnabled(R)
	actCount += 1
	ok = sut.safely(act)
	propok = sut.check()
	if (not ok) or ((not propok) and (config.check)):
		failure()
	else:
		savingTest()
	return ok

def showRunning():
	global sut, start
	elapsed = time.time() - start
	if sut.newBranches() != set([]):
		for b in sut.newBranches():
			print elapsed, len(sut.allBranches()), "New branch", b
	if sut.newStatements() != set([]):
		for s in sut.newStatements():
			print elapsed, len(sut.allStatements()), "New statement", s
	return

def main():
	global config, R, sut, bugs, ntest, start
	global actCount, branchCount, statementCount
	global savedTest, savedFlag

	parsed_args, parser = parse_args()
	config = make_config(parsed_args, parser)
	print('Testing using config={}'.format(config))

	R = random.Random(config.seed)
	sut = sut.sut()

	if config.silence:
		sut.silenceCoverage()
	
	bugs = 0
	actCount = 0
	branchCount = {}
	statementCount = {}
	ntest = 0

	start = time.time()
	elapsed = time.time() - start
	
	print "Starting Phase 1"
	if elapsed < config.timeout:
		sut.restart()
		ntest += 1
		for i in xrange(0, config.depth):
			if not randomAct():
				break
			elapsed = time.time() - start
			if config.running:
				showRunning()
			elapsed = time.time() - start
			if elapsed > config.timeout:
				print "Stopping test [TIMEOUT]"
				break
		collectCoverage()
	print "Finishing Phase 1"

	print "Starting Phase 2"
	elapsed = time.time() - start
	while elapsed < config.timeout:
		sut.restart()
		ntest += 1
		savedTest = None
		if (savedTest != None) and (R.random() > 0.7):
			sut.backtrack(savedTest)
			savedFlag = False

		for i in xrange(0, config.depth):
			if not randomAct():
				break
			elapsed = time.time() - start
			if config.running:
				showRunning()
			elapsed = time.time() - start
			if elapsed > config.timeout:
				print "Stopping test [TIMEOUT]"
				break
		collectCoverage()
		elapsed = time.time() - start
	print "Finishing Phase 2"

	if time.time() - start > config.timeout:
		print "[TIMEOUT]"

	if config.coverdetail:
		printCoverage()

	if config.coverage:
		sut.internalReport()

	if config.resultdetail:
		print "Covered", len(sut.allBranches()), "branches"
		print "Covered", len(sut.allStatements()), "statements"
	
		print "Failed", bugs, "times"
		print "Total tests", ntest
		print "Total actions", actCount
		print "Total runtime", time.time() - start
	
if __name__ == '__main__':
	main()

