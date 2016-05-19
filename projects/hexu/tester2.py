import sys
import random
import sut
import time

def collectCoverage():
    global coverageCount
    for s in sut.currStatements():
        if s not in coverageCount:
            coverageCount[s] = 0
        coverageCount[s] += 1 

def findBelowMean():
    global belowMean

    belowMean = set([])
    sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])

    coverSum = sum(coverageCount.values())
    coverMean = coverSum / (1.0*len(coverageCount))
  
    for s in sortedCov:   	
        if coverageCount[s] < coverMean:
            belowMean.add(s)
        else:
            break

def buildActivePool():
    global activePool
    findBelowMean()
    activePool = []
    for (t,c) in fullPool:
        for s in c:
            if s in belowMean:
                activePool.append((t,c))
                break
	#print len(activePool),"TESTS IN THE ACTIVE POOL,",len(fullPool),"IN FULL POOL"  

Timeout  = int(sys.argv[1])
Seed 	 = int(sys.argv[2])
Depth 	 = int(sys.argv[3])
Width  	 = int(sys.argv[4])
Faults   = int(sys.argv[5])
Coverage = int(sys.argv[6])
Running  = int(sys.argv[7])

rgen = random.Random()
rgen.seed(Seed)

sut = sut.sut()

start = time.time()

bugs = 0

acts = 0

coverageCount = {}
activePool = []
fullPool = []
belowMean = set([])
explore = 0.7

#for m in xrange(0,Width):
while time.time() - start < Timeout/5 :
	sut.restart()
	for t in xrange(0,Depth):
		if time.time() - start > Timeout:
			break
		act = sut.randomEnabled(rgen)
		ok  = sut.safely(act)
		collectCoverage()
		if len(sut.newStatements()) != 0:
			fullPool.append((list(sut.test()), set(sut.currStatements())))
		if not ok :
			bugs += 1
			if Faults :
				R = sut.reduce(sut.test(),sut.fails, True, True)
				i = 0
				result = ""
				for (s,_,_) in R :
					steps  = "# STEP " + str(i)
					result +=  sut.prettyName(s).ljust(80 - len(steps),' ') + steps + "\n"
					i += 1
				output = open("failure" + str(bugs) + ".test",'w')
				output.write("FOUND A FAILURE \n " + str(sut.failure()) + "\nREDUCING \n" + result + str(sut.failure()) + "\n" )
				output.close
			break
		if Running :

			if sut.newBranches() != set([]):
				print "ACTION:", act[0]
				elapsed = time.time() - start
				for b in sut.newBranches():
					print elapsed,len(sut.allBranches()),"New branch",b
	collectCoverage()

 
#for m in xrange(0,Width):
while time.time() - start < Timeout :
	if time.time() - start > Timeout:
		break
	buildActivePool()
	sut.restart()
	for t in xrange(0,Depth):
		if time.time() - start > Timeout:
			break
		act = sut.randomEnabled(rgen)
		ok  = sut.safely(act)
		if rgen.random() > explore:
			sut.replay(rgen.choice(activePool)[0])
		if Running :
			if sut.newBranches() != set([]):
				print "ACTION:", act[0]
				elapsed = time.time() - start
				for b in sut.newBranches():
					print elapsed,len(sut.allBranches()),"New branch",b
		
		acts += 1
		collectCoverage()
		if not ok :
			bugs += 1
			
			if Faults :
				R = sut.reduce(sut.test(),sut.fails, True, True)
				i = 0
				result = ""
				for (s,_,_) in R :
					steps  = "# STEP " + str(i)
					result +=  sut.prettyName(s).ljust(80 - len(steps),' ') + steps + "\n"
					i += 1
				output = open("failure" + str(bugs) + ".test",'w')
				output.write("FOUND A FAILURE \n " + str(sut.failure()) + "\nREDUCING \n" + result + str(sut.failure()) + "\n" )
				output.close
			break
		
	collectCoverage()
if Coverage :
	sut.internalReport()
print  bugs, "FAILED"
print "ACTIONS  : ", acts
print "RUN TIME : ", time.time() - start

#python tester1.py 30 1 100 1 0 1 1

#This will test sut.py for 30 seconds, with tests of maximum length
#100, a very narrow width (1), and not report or check for failures.
#It will collect and output an internal coverage report, and also
#report each new branch as it is discovered.
