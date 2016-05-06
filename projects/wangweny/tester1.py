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

def main():
	global config, R, sut, fails, actCount
	parsed_args, parser = parse_args()
	config = make_config(parsed_args, parser)

	R = random.Random(config.seed)

	sut = sut.sut()

	sut.silenceCoverage()
	
	fails = 0
	actCount = 0

	if config.faults:
		test_file = open("failure1.test", "w")
	
	start = time.time()
	elapsed = time.time() - start
	
	for i in xrange(0, config.depth):
		sut.restart()
		for j in xrange(0, config.width):
			act = None
			
			act = sut.randomEnabled(R)
			actCount += 1
			
			if act == None:
				print "No enabled actions"
					
			elapsed = time.time() - start
			if config.running:
				if sut.newBranches() != set([]):
					for b in sut.newBranches():
						print elapsed, len(sut.allBranches()), "New branch", b

				if sut.newStatements() != set([]):
					for s in sut.newStatements():
						print elapsed, len(sut.allStatements()), "New statement", s
	
			if elapsed > config.timeout:
				print "Stopping test [TIMEOUT]"
				break
				
			ok = sut.safely(act)
			propok = sut.check()
			if ((not ok) or (not propok)):
				fails += 1
				if config.faults == 1:
					test_file.write(str(sut.failure()) + "\n")
				R = sut.reduce(sut.test(), sut.fails, True, True)
				sut.prettyPrintTest(R)
				print sut.failure()
				sut.restart()
	
	if config.faults:
		test_file.close()
	
	if config.coverage:
		sut.restart()
		sut.report("coverage.out")
	
	print "Covered", len(sut.allBranches()), "branches"
	print "Covered", len(sut.allStatements()), "statements"
	
	print "Failed", fails, "times"
	print "Total actions", actCount
	print "Total runtime", time.time() - start

	
	#sut.internalReport()
	
if __name__ == '__main__':
	main()

