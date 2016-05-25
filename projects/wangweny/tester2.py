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
	parser.add_argument('timeout', type = int, default = 300, help = 'Timeout in seconds (300 default).')
	parser.add_argument('seed', type = int, default = None, help = 'Random seed (default = None).')
	parser.add_argument('depth', type = int, default = 10, help = 'Maximum search depth (10 default).')
	parser.add_argument('width', type = int, default = 10, help = 'Maximum search width (10 default).')
	parser.add_argument('faults', type = int, default = 0, help = 'Faults display (default = 0).')
	parser.add_argument('coverage', type = int, default = 0, help = 'Coverage display (default = 0).')
	parser.add_argument('running', type = int, default = 0, help = 'Running display (default = 0).')
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
    global coverageCount, branchCount, statementCount
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
	branMean = sum(branchCount.values())
	print "Mean Branches is", branMean
	for s in sortedBran:
		print s, branchCount[s]

	sortedStat = sorted(statementCount.keys(), key = lambda x : statementCount[x])
	stateMean = sum(statementCount.values())
	print "Mean statements is", stateMean
	for s in sortedStat:
		print s, statementCount[s]

def randomAct():
	global actCount, bugs, R, failPool
	act = None
	act = sut.randomEnabled(R)
	actCount += 1

	ok = sut.safely(act)

	if (not ok):
		bugs += 1
		collectCoverage()
		R = sut.reduce(sut.test(), sut.fails, True, True)
		if config.faults :
			filename = 'failure%d.test'%bugs
			sut.saveTest(sut.test(), filename)
		sut.prettyPrintTest(R)

		sut.restart()

	return ok

def main():
	global config, R, sut, bugs, actCount, coverageCount, branchCount, statementCount, test_file, ntest

	parsed_args, parser = parse_args()
	config = make_config(parsed_args, parser)
	print('Testing using config={}'.format(config))

	R = random.Random(config.seed)
	sut = sut.sut()

	sut.silenceCoverage()
	
	bugs = 0
	actCount = 0
	coverageCount = {}
	branchCount = {}
	statementCount = {}
	ntest = 0
	
	start = time.time()
	elapsed = time.time() - start
	
	while elapsed < config.timeout:
		sut.restart()
		ntest += 1
		for i in xrange(0, config.depth):
			for j in xrange(0, config.width):
				if randomAct():
					preTest = sut.state()
				else:
					sut.backtrack(preTest)

				elapsed = time.time() - start
				if config.running:
					if sut.newBranches() != set([]):
						for b in sut.newBranches():
							print elapsed, len(sut.allBranches()), "New branch", b
					if sut.newStatements() != set([]):
						for s in sut.newStatements():
							print elapsed, len(sut.allStatements()), "New statement", s
			
				elapsed = time.time() - start
				if elapsed > config.timeout:
					print "Stopping test [TIMEOUT]"
					break
			
			elapsed = time.time() - start
			if elapsed > config.timeout:
				break
		collectCoverage()
		elapsed = time.time() - start

	printCoverage()

	if config.coverage:
		sut.internalReport()

	print "Covered", len(sut.allBranches()), "branches"
	print "Covered", len(sut.allStatements()), "statements"
	
	print "Failed", bugs, "times"
	print "Total tests", ntest
	print "Total actions", actCount
	print "Total runtime", time.time() - start
	
	#sut.internalReport()
	
if __name__ == '__main__':
	main()

