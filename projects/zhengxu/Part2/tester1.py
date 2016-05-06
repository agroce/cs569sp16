# CS569 - Milestone #1
# Name: Xu Zheng
# Onid: zhengxu
# May 5, 2016

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
						help='Either 0 or 1 (default = 1) depending on whether check for faults.')
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

sut = sut.sut()

def main():
	global config,rgen,actCount,failCount,ntests,coverageCount

	parsed_args, parser = parse_args()
	config = make_config(parsed_args, parser)
	rgen = random.Random(config.seed)

	actCount = 0
	failCount = 0
	coverageCount = {}

	start = time.time()
	ntests = 0
	while True:
		elapsed = time.time() - start
		if elapsed > config.timeout:
			print "STOPPING TEST DUE TO TIMEOUT, TERMINATED AT LENGTH",ntests
			break

		for i in xrange(0, config.depth):
			sut.restart()
			ntests += 1
			for j in xrange(0, config.width):
				act = sut.randomEnabled(rgen)
				actCount += 1
				ok = sut.safely(act)
				if not ok:
					failCount += 1
					print "FOUND A FAILURE"
					collectCoverage()
					R = sut.reduce(sut.test(),sut.fails, True, True)
					sut.prettyPrintTest(R)
					print sut.failure()
					break

				if config.running:
					if sut.newBranches() != set([]):
						for b in sut.newBranches():
							print time.time()-start, len(sut.allBranches()), "New branch", b
					if sut.newStatements() != set([]):
						for s in sut.newStatements():
							print time.time()-start,len(sut.allStatements()),"New statement",s

		collectCoverage()	

	if config.faults:
		print "TOTAL FAULTS", failCount

	if config.coverage:
		print len(sut.allBranches()),"BRANCHES COVERED"
		print len(sut.allStatements()),"STATEMENTS COVERED"

	sut.internalReport()
	
	print "TOTAL ACTIONS",actCount
	print "TOTAL RUNTIME",time.time()-start

if __name__ == '__main__':
	main()