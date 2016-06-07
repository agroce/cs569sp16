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

def Find_bugs(list_actions):
	# print "Find_bugs"
	global coverage_counter
	global bugs	
	global Record
	global string
	safe = sut.safely(list_actions)
	# running_oh()
	if not safe:
		bugs = bugs + 1
		print " *** find a bug: ",bugs
		# bugs = bugs + 1
		for t in sut.currStatements():
			if t not in coverage_counter:
				coverage_counter[t]=0
			coverage_counter[t] = coverage_counter[t] + 1	
		# Collect_coverage()
		print sut.failure()
		# string = str(sut.failure)
		Record = True
		print "reducing..."
		R = sut.reduce(sut.test(),sut.fails, True, True)
		sut.prettyPrintTest(R)	
		# record_failures(R)
		if FAULTS:
			print"create file"
			# for x in xrange(1,bugs):
				# print "save"
			sut.saveTest(R, failure + str(bugs)+ ".test")
			# filename = "failure" +  str(bugs) + ".test"
			# sut.saveTest(sut.test(), filename)
		# sut.restart()
	else:
		running_oh()

	return safe

def divide_coverage():
	global four_coverage,three_coverage, two_coverage, four_coverage
	global median_even, median_odd
	
	sort = sorted(coverage_counter.keys(),key=lambda x: coverage_counter[x] )
	length_sort	= len(coverage_counter)
	count =0
	count_odd =0
	# print "length_sort: ", length_sort
	# print "sort: ", sort
	a = length_sort/2
	# print "a ",a

	# b = (length_sort/2) - 1
	# for s in sort:
	if length_sort % 2 == 0:  
		for s in sort:
			count =count + 1
			# if s in xrange(data_list[index]):
			median_even.add(s)
			if count == a:					
				break;

	if not length_sort % 2 == 0: 
		for s in sort:
			count_odd =count_odd + 1
			# if s in xrange(data_list[index]):
			median_odd.add(s)
			if count_odd == a +1:					
				break;
	# 	return (sort[ length_sort/2 ] + sort[length_sort/2 - 1]) / 2.0
	# return sort[length_sort /2 ]
	# print ">>> median_odd: ", median_odd
	# print ">>> median_even ", median_even

def running_oh():
	global actinos, elapsed, lastAddCoverage, median_even, median_odd 


	if len(sut.newBranches()) != set ([]):
		print "ACTION:", list_actions[0]
		for s in sut.newBranches():
			print elapsed,len(sut.allBranches()),"New branch",s

	if len(sut.newStatements())> 0:
		print "ACTION:", list_actions[0]
		for s in sut.newStatements():
			print elapsed,len(sut.allStatements()),"New statement",s

		old_test = list(sut.test())
		store_new_test  = sut.reduce(old_test,sut.coversStatements(sut.newStatements()))
		sut.replay(old_test)
		testBuffer.append(store_new_test)	
		currentStatementBuffer.append(set(sut.currStatements()))
		lastAddCoverage = set(sut.currStatements())
		

	for s in median_odd or median_even:
		if s in sut.currStatements() and s not in lastAddCoverage:
			print "find new path to lower coverstatements: ", s
			testBuffer.append(list(sut.test()) )
			currentStatementBuffer.append(set(sut.currStatements()))
			lastAddCoverage = set(sut.currStatements() )


def exploit():
	global activebuffer
	# print "==== ",activebuffer
	# activebuffer = []
	# print "even", median_even
	# print "odd" ,median_odd
	# print "current statement buffer:", currentStatementBuffer
	for s in currentStatementBuffer:
		# print ">>>median_even: ",median_even
		for s in median_even:
			activebuffer.append(s)

		for s in median_odd:
			activebuffer.append(s)
	print "<<length of activebuffer>> : ", len(activebuffer)

sut = sut.sut()

sut.silenceCoverage()
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
failure = "failure"
actinos = None

testBuffer = []
currentStatementBuffer = []
activebuffer = []

four_coverage = set([])
three_coverage= set([])
two_coverage  = set([])
one_coverage  = set([])


median_even = set([])
median_odd = set([])


while time.time() - start_time_1 < (TIMEOUT*0.5):
	sut.restart()
	for dep in xrange(1,DEPTH):
		dep = dep +1 
		queue_list =[]
		inside_time = time.time()
		# sut.restart()
		for x in queue_q:
			ran_queue.append(x)
			sut.backtrack(x)
			elapsed = time.time() - start_time_1
			list_actions = sut.randomEnabled(regn)
			# print "list_actions>>>>",list_actions
			# list_actions = sut.enabled()
			# actinos = list_actions
			# regn.shuffle(list_actions)	
			# Find_bugs(list_actions)
			# for a in list_actions:
			Find_bugs(list_actions)	
			divide_coverage()
			if time.time() - inside_time >= 2:
				break
			# Find_bugs(list_actions)	
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






start_time_2 = time.time()
while time.time() - start_time_2 < (TIMEOUT*0.4):
 	exploit()
 	inside_time = time.time()
 	# print ">>>activebuffer: ",activebuffer
# 	lastAddCoverage = set([])
	# sut.restart()
	sut.state()
	sut.replay(regn.choice(testBuffer),regn.choice(activebuffer)[0])
	act = sut.randomEnabled(regn)
 	Find_bugs(act)
 	if time.time() - inside_time >= 2:
		break
	for s in sut.currStatements():
			if s not in coverage_counter:
				coverage_counter[s]=0
			coverage_counter[s] = coverage_counter[s] + 1		

		

if COVERAGE:
	sut.internalReport()

if RUNNING:
	running_oh()


if Record == False:
	print"no bugs into record file... "


print "depth:", dep
# coverage_counter is statement_counter 
print "*** coverage_counter is : ***", len(coverage_counter)
print "*** failed ***",bugs
print "***total running time ***",time.time()-start_time_1