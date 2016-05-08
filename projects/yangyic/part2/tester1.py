import sut
import random
import math
import sys 
import time

TIMEOUT = int(sys.argv[1])
SEED = int(sys.argv[2])
DEPTH = int(sys.argv[3])
WIDTH = int(sys.argv[4])
FAULTS = int(sys.argv[5])
COVERAGE = int(sys.argv[6])
RUNNING = int(sys.argv[7])

def Find_bugs(a):
	#print "aaaaa"
	global coverage_counter
	global bugs
	global Record
	global string
	safe = sut.safely(a)
	running_oh()
	if not safe:
		print " *** find a bug: "
		bugs = bugs + 1
		for s in sut.currStatements():
			if s not in coverage_counter:
				coverage_counter[s]=0
			coverage_counter[s] = coverage_counter[s] + 1	
		# Collect_coverage()
		print sut.failure()
		# string = str(sut.failure)
		record_failures()
		Record = True
		# R = sut.reduce(sut.test(),sut.fails, True, True)
		# sut.prettyPrintTest(R)	
		sut.restart()


def divide_coverage():
	global four_coverage,three_coverage, two_coverage, one_coverage
	
	# sort = sorted(coverage_counter.keys(),key=lambda x: coverage_counter[x] )
	# length_sort	= len(coverage_counter)
	# print "length_sort: ", length_sort
	# a = length_sort/2
	# b = (length_sort/2) - 1
	# for s in sort:
	# 	if length_sort % 2:


	# if not length_sort % 2 :
	# 	return (sort[ length_sort/2 ] + sort[length_sort/2 - 1]) / 2.0
	# return sort[length_sort /2 ]


def running_oh():
	if len(sut.newStatements())> 0:
		print "*** find a new statement: ",sut.newStatements()
	if len(sut.newBranches())> 0:
		print "*** find a new branch :", sut.newBranches()

def record_failures():
	global string
	file = open("record_failures.txt","w")
	file.write(str(sut.failure()))
	# file.write(string)



# <timeout> <seed> <depth> <width> <faults> <coverage> <running>

sut = sut.sut()
nums = random.Random() 
bugs = 0
coverage_counter = {}
string = {} 


elapsed=0
dep=0
length_cover=0

regn = random.Random()
regn.seed(SEED)
queue_q = [sut.state()]  
ran_queue = []
visited = []
start_time_1 = time.time()
Record = False


four_coverage = set([])
three_coverage= set([])
two_coverage  = set([])
one_coverage  = set([])



while time.time() - start_time_1 < (TIMEOUT*0.87):
	# for dep in xrange(1,DEPTH):
		dep = dep +1 
		queue_list =[]
		inside_time = time.time()
		sut.restart()
		for x in queue_q:
			ran_queue.append(x)
			sut.backtrack(x)
			list_actions = sut.enabled()
			regn.shuffle(list_actions)	
			for a in list_actions:
				divide_coverage()
				if time.time() - inside_time >= 3:
					break
				Find_bugs(a)	
				s2 = sut.state()
				if s2 not in ran_queue:	
					ran_queue.append(s2)
					queue_list.append(s2)	
				sut.backtrack(x)	
			# Collect_coverage()	
			for s in sut.currStatements():
				if s not in coverage_counter:
					coverage_counter[s]=0
				coverage_counter[s] = coverage_counter[s] + 1	
		queue_q = queue_list
		

if COVERAGE:
	sut.internalReport()

if RUNNING:
	running_oh()

if FAULTS:
	record_failures()	
	if Record == False:
		print"no bugs into record file... "


print "depth:", dep
# coverage_counter is statement_counter 
print "*** coverage_counter is : ***", len(coverage_counter)
print "*** failed ***",bugs
print "***total running time ***",time.time()-start_time_1
