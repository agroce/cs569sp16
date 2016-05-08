import math
import random
import sys
import sut
import time
import os


TimeOut = int(sys.argv[1])
Seed = int(sys.argv[2])
Depth = int(sys.argv[3])
Width = int(sys.argv[4])
Faults = int(sys.argv[5])
Coverage = int(sys.argv[6])
Running = int(sys.argv[7])

sut = sut.sut()
sut.silenceCoverage()
rand = random.Random()
rand.seed(Seed)

Failure_Report = "Fail"

def randomOperation():
	global Num_Bug = 0
	global Time_Start
	Operation = sut.randomEnabled(rand)
	Good = sut.safely(Operation)
	Runtime = time.time() - Time_Start

	if (Running):
		if ((len(sut.newBranches())) > 0):
			print "Operation: ", Operation[0]
			for i in sut.newBranches():
				print "Runtime: ", round(Runtime, 3), "| All Branches: ", len(sut.allBranches()), "| New Branch: ", i
			print "=========================================================="

	if (not Good):
		Num_Bug += 1
		print "BUG FOUND! Num: ", Num_Bug
		print sut.failure()
		print "=========================================================="
		print "***Reducing ..."
		reduce = sut.reduce(sut.test(), sut.fails, True, True)
		sut.prettyPrintTest(reduce)
		print sut.failure()
		print "=========================================================="

		if (Faults):
			file = open((Failure_Report + str(Num_Bug) + ".test"), "w")
			print >> file, sut.failure()

			i = 1
			for (reducing, _, _) in reduce:
				Step_Reduce = "#" + str(i) + "STEP"
				print >> file, sut.prettyName(reducing).ljust(100 - len(Step_Reduce), ' '), Step_Reduce
				i += 1
			file.close()

	return Good, Num_Bug


def mian():
	CoverageCount = {}
	NS = []
	NSM = []
	CS = []
	KC =[]
	Time_Start = time.time()
	Phase1_Time_Budget = TimeOut / 3

	print "***PHASE 1 Starting ..."
	print "=========================================================="

	while (time.time() < (Time_Start + Phase1_Time_Budget)):
		sut.restart()
		for d in xrange(0, Depth):
			Good, bugNum = randomOperation()
			if (len(sut.newStatements()) > 0):
				NS.append(sut.state())
				NSM.append(sut.newStatements())

			if (not Good):
				break

		for s in sut.currStatements():
			if s not in CoverageCount:
				CoverageCount[s] = 0
			CoverageCount[s] += 1

	sorted_Coverage = sorted(CoverageCount.keys(), key = lambda x: CoverageCount[x])

	sum_value = 0
	for s in sorted_Coverage:
		sum_value += CoverageCount[s]

	mean_value = sum_value / len(CoverageCount)

	temp_sum = 0.0
	for s in sorted_Coverage:
		temp_sum += math.pow(CoverageCount[s] - mean_value, 2)

	STD = math.sqrt(temp_sum / len(CoverageCount))
	Threshold = mean_value - (0.6 * STD)
	print "Mean: ", mean_value
	print "Standard Deviation: ", round(STD, 3)
	print "Threshold: ", round(Threshold, 3)
	print "=========================================================="

	for s in sorted_Coverage:
		if (CoverageCount[s] > Threshold):
			break
		for k in KC:
			if s in NSM[k]:
				continue
		for k in xrange(0, len(NSM)):
			if s in NSM[k]:
				KC.append(k)

	for k in KC:
		CS.append(NS[k])

	print bugNum, "BUGS FOUND!!!"

	for s in sorted_Coverage:
		print s, CoverageCount[s]
	print "=========================================================="

	if (Coverage == 1):
		sut.internalReport()

	print ""
	print "***PHASE 2 Starting..."
	print "=========================================================="

	Phase2_Time_Budget = TimeOut - Phase1_Time_Budget
	Time_Start = time.time()
	i = 1
	while (time.time() < (Time_Start + Phase2_Time_Budget)):
		for s in CS:
			i += 1
			temp_time = Phase2_Time_Budget / (len(CS) * i)
			time_start_2 = time.time()

			while (time.time() < time_start_2 + temp_time):
				sut.restart()
				sut.backtrack(s)

				for d in xrange(0, Depth):
					Good, bugNum = randomOperation()
					if (len(sut.newStatements()) > 0):
						print "FOUND New Statements!!!"
						CS.insert(i, sut.state())

					if (not Good):
						break

				for j in sut.currStatements():
					if j not in CoverageCount:
						CoverageCount[j] = 0
					CoverageCount[j] += 1

			sorted_Coverage = sorted(CoverageCount.keys(), key = lambda x: CoverageCount[x])

	print bugNum, "BUGS FOUND!!!"

	for s in sorted_Coverage:
		print s, CoverageCount[s]
	print "=========================================================="

	if (Coverage == 1):
		sut.internalReport()


if __name__ == '__main__':
	main()

