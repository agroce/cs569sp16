import math
import random
import sys
import sut
import time
import os


timeout = int(sys.argv[1])
seed = int(sys.argv[2])
depth = int(sys.argv[3])
width = int(sys.argv[4])
faults = int(sys.argv[5])
coverage = int(sys.argv[6])
running = int(sys.argv[7])

sut = sut.sut()
sut.silenceCoverage()
rand = random.Random()
rand.seed(seed)

coverageCount = {}

new_state = []
new_statement = []

chosen_state = []
k_chosen = []

state_queue = []
state_visited = []

fail = "fail"
bug_num = 0

def randomOperation():
	global bug_num, time_start
	operation = sut.randomEnabled(rand)
	good = sut.safely(operation)
	runtime = time.time() - time_start

	if (running):
		if (len(sut.newBranches())) > 0
		print "Operation: ", operation[0]
		for i in sut.newBranches():
			print runtime, len(sut.allBranches()), "New Branch", i

	if (not good):
		bug_num += 1
		print "A bug is found! #", bug_num
		print sut.failure()
		print ("Reducing!")
		reduce = sut.reduce(sut.test(), sut.fails, True, True)
		sut.prettyPrintTest(reduce)
		print(sut.failure())

		if (faults):
			f = open((fail + str(bug_num) + ".test"), "w")
			print >> f, sut.failure()

			j = 0
			for (s_reduce, _, _) in reduce:
				steps_reduce = "# Step " + str(j)
				print >> f, sut.prettyName(s_reduce).ljust(80 - len(steps_reduce), ' '), steps_reduce
				j += 1
			f.close()
		print "Time: ", runtime
	return good

time_start = time.time()
current_depth = 1
state_queue = [sut.state()]

Time_Phase1 = timeout / 4
print "PHASE 1 ..."
while (time.time() < (time_start + Time_Phase1)):
	sut.restart()
	for d in xrange(0, depth):
		good = randomOperation()
		if (not good):
			break
		if (len(sut.newStatements()) > 0):
			new_state.append(sut.state())
			new_statement.append(sut.newStatements())

	for s in sut.currStatements():
		if s not in coverageCount:
			coverageCount[s] = 0
		coverageCount[s] += 1

sortedCoverage = sorted(coverageCount.keys(), key = lambda x: coverageCount[x])

sum_value = 0
for s in sortedCoverage:
	sum_value += coverageCount[s]

mean_value = sum_value / len(coverageCount)
sum_value = 0.0
for s in sortedCoverage:
	sum_value += math.pow(coverageCount[s] - mean_value, 2)
sum_value = sum_value / (len(coverageCount) - 1)

std = math.sqrt(sum_value)
threshold = mean_value - (0.67 * std)
print "Mean: ", mean_value
print "Standard Deviation: ", std
print "Threshold: ", threshold

for s in sortedCoverage:
	if (coverageCount[s] > threshold):
		break
	for k in k_chosen:
		if s in new_statement[k]:
			continue
	for k in xrange(0, len(new_statement)):
		if s in new_statement[k]:
			k_chosen.append(k)

for k in k_chosen:
	chosen_state.append(new_state[k])

print bug_num, " Bugs Found!"

for s in sortedCoverage:
	print s, coverageCount[s]
if (coverage):
	sut.internalReport()


print "PHASE 2 ..."
Time_Phase2 = timeout - Time_Phase1

all_state = []
new_statement = []
i = 0;
time_start = time.time()
while (time.time() < (time_start + Time_Phase2)):
	for state in chosen_state:
		i += 1
		time_state = float(Time_Phase2) / (len(chosen_state) * (i + 1))
		time_start2 = time.time()
		while (time.time() < time_start2 + time_state):
			sut.restart()
			sut.backtrack(state)
			for d in xrange(0, depth):
				good = randomOperation()
				if (not good):
					break
				if (len(sut.newStatements()) > 0):
					print "A New Statement is Found!"
					chosen_state.insert(i, sut.state())

			for s in sut.currStatements():
				if s not in coverageCount:
					coverageCount[s] = 0
				coverageCount[s] += 1

		sortedCoverage = sorted(coverageCount.keys(), key = lambda x: coverageCount[x])

print bug_num, " Bugs Found!"

for s in sortedCoverage:
	print s, coverageCount[s]

if (coverage):
	sut.internalReport()

