# CS569 - Milestone #2
# Name: Xu Zheng
# Onid: zhengxu
# May 18, 2016

import sys
import sut
import random
import time
import argparse
from collections import namedtuple

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('timeout', type=int, default=30,
						help='Timeout in seconds (default = 30) for testing.')
	parser.add_argument('seed', type=int, default=None,
						help='Random seed (default = None).')
	parser.add_argument('depth', type=int, default=100,
						help='Maximum length of a test (default = 100).')
	parser.add_argument('width', type=int, default=1,
						help='Maximum search width (default = 1).')
	parser.add_argument('faults', type=int, default=0,
						help='Either 0 or 1 (default = 0) depending on whether check for faults.')
	parser.add_argument('coverage', type=int, default=1,
						help='Either 0 or 1 (default = 1) depending on whether produce a coverage report.')
	parser.add_argument('running', type=int, default=1,
						help='Either 0 or 1 (default = 1) depending on whether produce running info on branch.')
	parsed_args = parser.parse_args(sys.argv[1:])
	return (parsed_args, parser)

def make_config(pargs, parser):
	pdict = pargs.__dict__
	key_list = pdict.keys()
	arg_list = [pdict[k] for k in key_list]
	Config = namedtuple('Config', key_list)
	nt_config = Config(*arg_list)
	return nt_config

def collectCoverage():
	global coverageCount

	for s in sut.currStatements():
		if s not in coverageCount:
			coverageCount[s] = 0
		coverageCount[s] += 1    

def buildSecondPool():
	global secondPool

	belowMean = set([])
	sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])
	coverSum = sum(coverageCount.values())
	coverMean = coverSum / (1.0*len(coverageCount))
	for s in sortedCov:
		if coverageCount[s] < coverMean:
			belowMean.add(s)
		else:
			break

	secondPool = []
	for (t,c) in firstPool:
		for s in c:
			if s in belowMean:
				secondPool.append((t,c))
				break

def expandPool():
	if len(sut.newStatements()) != 0:
		firstPool.append((list(sut.test()), set(sut.currStatements())))

def saveTests(failCount):
	filename = 'failure' + `failCount` + '.test'
	ft = open(filename, 'a')
	ft.write(str(sut.failure()))
	ft.close()

sut = sut.sut()

def main():
	global config,rgen,actCount,failCount,ntests,firstPool,coverageCount

	parsed_args, parser = parse_args()
	config = make_config(parsed_args, parser)
	rgen = random.Random(config.seed)

	actCount = 0
	failCount = 0
	coverageCount = {}
	firstPool = []

	start = time.time()
	ntests = 0
	while time.time() - start < (config.timeout)/2:
		ntests += 1
		sut.restart()
		for d in xrange(0, config.depth):
			act = sut.randomEnabled(rgen)
			actCount += 1

			ok = sut.safely(act)
			expandPool()
			if config.running:
				if sut.newBranches() != set([]):
					print "ACTION:", act[0]
					for b in sut.newBranches():
						print time.time()-start, len(sut.allBranches()), "New branch", b
				if sut.newStatements() != set([]):
					print "ACTION:", act[0]
					for s in sut.newStatements():
						print time.time()-start, len(sut.allStatements()),"New statement",s

			if not ok:
				failCount += 1
				if config.faults:
					saveTests(failCount)
				print "FOUND A FAILURE"
				R = sut.reduce(sut.test(),sut.fails, True, True)
				sut.prettyPrintTest(R)
				print sut.failure()
				sut.restart()
				break

			if time.time() - start > (config.timeout)/2:
				print "FIRST POOL HAS BEEN CREATED, TERMINATED AT LENGTH",ntests
				break
		collectCoverage()

	end = time.time()
	while time.time() - end < (config.timeout)/2:
		buildSecondPool()
		sut.restart()
		if rgen.random() > 0.5:
			sut.replay(rgen.choice(secondPool)[0])
		ntests += 1
		for d in xrange(0, config.depth):
			act = sut.randomEnabled(rgen)
			actCount += 1

			ok = sut.safely(act)
			expandPool()
			if config.running:
				if sut.newBranches() != set([]):
					print "ACTION:", act[0]
					for b in sut.newBranches():
						print time.time()-end, len(sut.allBranches()), "New branch", b
				if sut.newStatements() != set([]):
					print "ACTION:", act[0]
					for s in sut.newStatements():
						print time.time()-end, len(sut.allStatements()),"New statement",s

			if not ok:
				failCount += 1
				if config.faults:
					saveTests(failCount)
				print "FOUND A FAILURE"
				R = sut.reduce(sut.test(),sut.fails, True, True)
				sut.prettyPrintTest(R)
				print sut.failure()
				sut.restart()
				break

			if time.time() - end > (config.timeout)/2:
				print "STOPPING TEST DUE TO TIMEOUT, TERMINATED AT LENGTH",ntests
				break
		collectCoverage()

	if config.faults:
		print "TOTAL FAULTS", failCount

	if config.coverage:
		sut.internalReport()
	
	print "TOTAL ACTIONS",actCount
	print "TOTAL RUNTIME",time.time()-start

if __name__ == '__main__':
	main()