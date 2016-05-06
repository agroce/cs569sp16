import sut
import random
import statistics
import math
import sys 
import time

def Find_bugs(a):
	#print "aaaaa"
	global coverage_counter
	global bugs
	safe = sut.safely(a)
	if not safe:
		print " find a bug: "
		bugs = bugs + 1
		for s in sut.currStatements():
			if s not in coverage_counter:
				coverage_counter[s]=0
			coverage_counter[s] = coverage_counter[s] + 1	
		print sut.failure()
		R = sut.reduce(sut.test(),sut.fails, True, True)
		sut.prettyPrintTest(R)	
# def Collect_coverage():


# <timeout> <seed> <depth> <width> <faults> <coverage> <running>

sut = sut.sut()
nums = random.Random() 
bugs = 0
coverage_counter = {}

TIMEOUT = int(sys.argv[1])
SEED = int(sys.argv[2])
DEPTH = int(sys.argv[3])
WIDTH = int(sys.argv[4])
FAULTS = int(sys.argv[5])
COVERAGE = int(sys.argv[6])
RUNNING = int(sys.argv[7])

average_time_dep = TIMEOUT/DEPTH
elapsed=0
dep=0
regn = random.Random()
queue_q = [sut.state()]  
ran_queue = []
visited = []
start_time_1 = time.time()


while time.time() - start_time_1 < TIMEOUT:
	# for dep in xrange(1,DEPTH):
		dep = dep +1 
		queue_list =[]
		inside_time = time.time()
		for x in queue_q:
			ran_queue.append(x)
			sut.backtrack(x)
			list_actions = sut.enabled()
			regn.shuffle(list_actions)		
			for a in list_actions:
				if time.time() - inside_time >= average_time_dep:
					break
				Find_bugs(a)	
				s2 = sut.state()
				if s2 not in ran_queue:	
					ran_queue.append(s2)
					queue_list.append(s2)	
				sut.backtrack(x)	
			for s in sut.currStatements():
				if s not in coverage_counter:
					coverage_counter[s]=0
				coverage_counter[s] = coverage_counter[s] + 1	
		queue_q = queue_list

if COVERAGE:
	sut.internalReport()
print "depth:", dep
print "*** coverage_counter is : ***",1.0*len(coverage_counter)
print "*** failed ***",bugs
print "***total running time ***",time.time()-start_time_1
