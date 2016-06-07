import sys
import random
import sut
import time
import argparse
from collections import namedtuple

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

def findParent():
	global parents 
	tempPool = []
	for (t,c) in activePool:
		tempPool.append(c)
	act1 = tempPool[random.randrange(0,len(tempPool))]
	tempPool.remove(act1)
	act2 = tempPool[random.randrange(0,len(tempPool))]
	flag1 = 0
	flag2 = 0
	for (t,c) in activePool :
		if c == act1 :	
			act1 = t 
			flag1 = 1
		if c == act2 :
			act2 = t
			flag2 = 1
		if flag1 + flag2 == 2 :
			break 	
	return (act1, act2)
def switchRandom(act1,act2):
	rdm1 = random.randrange(len(act1)/2,len(act1),1)
	rdm2 = random.randrange(len(act2)/2,len(act2),1)
	rdm = 0
	if rdm1 > rdm2  and  rdm1 < len(act2) :
		rdm = rdm1
	elif rdm1 < rdm2  and rdm2 < len(act1) :
		rdm = rdm2
	else :
		rdm = min (rdm1,rdm2)
	for num in range(1,rdm):
		tempRdm1 = random.randrange(1,len(act1),1)
		tempRdm2 = random.randrange(1,len(act2),1)
		tempAct = act1[tempRdm1]
		act1[tempRdm1] = act2[tempRdm2]
		act2[tempRdm2] = tempAct
	
	return (act1, act2)

def takeTest(actt):
	global fullPool,bugs,sut
	
	ok  = sut.safely(actt)
	collectCoverage()
	if len(sut.newStatements()) != 0:

		fullPool.append((list(sut.test()), set(sut.currStatements())))
	if not ok :
			bugs += 1
			if Faults :
				R = sut.reduce(sut.test(),sut.fails, True, True)
				filename = "failure" + str(bugs) + ".test"
				sut.saveTest(R,filename)
		

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--timeout', type = int, default = 10, help = 'Timeout in seconds.')
    parser.add_argument('-s', '--seed', type = int, default = 1, help = 'Random seed.')
    parser.add_argument('-d', '--depth', type = int, default = 100, help = 'For search depth.')                                                
    parser.add_argument('-w', '--width', type = int, default = 1, help = 'For the Width.')
    parser.add_argument('-f', '--fault', action = 'store_true', help = 'To check for fault')
    parser.add_argument('-c', '--coverage', action = 'store_true', help = 'To show coverage report')
    parser.add_argument('-r', '--running', action = 'store_true', help = 'To show running branch coverage report')
    parsed_args = parser.parse_args(sys.argv[1:])

    return (parsed_args, parser)

def make_config(pargs, parser):
    pdict = pargs.__dict__
    key_list = pdict.keys()
    arg_list = [pdict[k] for k in key_list]
    Config = namedtuple('Config', key_list)
    nt_config = Config(*arg_list)
    return nt_config  

(parsed_args, parser) = parse_args()
config = make_config(parsed_args, parser)

rgen = random.Random()
rgen.seed(config.seed)

sut = sut.sut()

start = time.time()

bugs = 0

acts = 0

flag = []

coverageCount = {}
activePool = []
fullPool = []
belowMean = set([])
explore = 0.7

#for m in xrange(0,Width):
while time.time() - start < config.timeout/5 :
	sut.restart()
	for t in xrange(0,config.depth):
		if time.time() - start > config.timeout:
			break
		act = sut.randomEnabled(rgen)
		flag = act
		ok  = sut.safely(act)
		collectCoverage()
		if len(sut.newStatements()) != 0:
			fullPool.append((list(sut.test()), set(sut.currStatements())))
		if not ok :
			bugs += 1
			if config.fault :
				R = sut.reduce(sut.test(),sut.fails, True, True)
				filename = "failure" + str(bugs) + ".test"
				sut.saveTest(R,filename)
				# i = 0
				# result = ""
				# for (s,_,_) in R :
				# 	steps  = "# STEP " + str(i)
				# 	result +=  sut.prettyName(s).ljust(80 - len(steps),' ') + steps + "\n"
				# 	i += 1
				# output = open("failure" + str(bugs) + ".test",'w')
				# output.write("FOUND A FAILURE \n " + str(sut.failure()) + "\nREDUCING \n" + result + str(sut.failure()) + "\n" )
				# output.close
			break
		if config.running :

			if sut.newBranches() != set([]):
				print "ACTION:", act[0]
				elapsed = time.time() - start
				for b in sut.newBranches():
					print elapsed,len(sut.allBranches()),"New branch",b
	collectCoverage()

#for m in xrange(0,Width):
while time.time() - start < config.timeout :
	if time.time() - start > config.timeout:
		break
	buildActivePool()
	sut.restart()
	
	fittest = []
	for (t,s) in activePool :
		fittest.append(t)
	lenFull = len(fullPool)
	while len(fittest) < lenFull:
		
		(act1, act2) = findParent()
		flag = 0
		flag1 = 1
		flag2 = 1
		(act1, act2) = switchRandom(act1,act2)
		for act in act1 :
			
			ok  = sut.safely(act)
			collectCoverage()
			if len(sut.newStatements()) != 0:
			
				fullPool.append((list(sut.test()), set(sut.currStatements())))
			if not ok :
					flag1 = 0
			if config.running :
				if sut.newBranches() != set([]):
					print "ACTION:", act[0]
					elapsed = time.time() - start
					for b in sut.newBranches():
						print elapsed,len(sut.allBranches()),"New branch",b
		for act in act2 :
			ok  = sut.safely(act)
			collectCoverage()
			if len(sut.newStatements()) != 0:
				
				fullPool.append((list(sut.test()), set(sut.currStatements())))
			if not ok :
					flag2 = 0
			if config.running :
				if sut.newBranches() != set([]):
					print "ACTION:", act[0]
					elapsed = time.time() - start
					for b in sut.newBranches():
						print elapsed,len(sut.allBranches()),"New branch",b
		if flag1 :
			fittest.append(act1)
			flag = 1
		if flag2 :
			fittest.append(act2)
			flag = 1
		if flag :
			buildActivePool()


	#sut.restart()
	for t in xrange(0,config.depth):
		if time.time() - start > config.timeout:
			break


		act = sut.randomEnabled(rgen)
		ok  = sut.safely(act)

		if rgen.random() > explore:
			sut.replay(rgen.choice(activePool)[0])
		
			if config.running :
				if sut.newBranches() != set([]):
					print "ACTION:", act[0]
					elapsed = time.time() - start
					for b in sut.newBranches():
						print elapsed,len(sut.allBranches()),"New branch",b
		
		acts += 1
		collectCoverage()
		if not ok :
			bugs += 1
			
			if config.fault :
				R = sut.reduce(sut.test(),sut.fails, True, True)
				filename = "failure" + str(bugs) + ".test"
				sut.saveTest(R,filename)
				# i = 0
				# result = ""
				# for (s,_,_) in R :
				# 	steps  = "# STEP " + str(i)
				# 	result +=  sut.prettyName(s).ljust(80 - len(steps),' ') + steps + "\n"
				# 	i += 1
				# output = open("failure" + str(bugs) + ".test",'w')
				# output.write("FOUND A FAILURE \n " + str(sut.failure()) + "\nREDUCING \n" + result + str(sut.failure()) + "\n" )
				# output.close
			break
		
	collectCoverage()
if config.coverage :
	sut.internalReport()
print "FAILED   : ", bugs
print "ACTIONS  : ", acts
print "RUN TIME : ", time.time() - start

#python tester1.py 30 1 100 1 0 1 1

#This will test sut.py for 30 seconds, with tests of maximum length
#100, a very narrow width (1), and not report or check for failures.
#It will collect and output an internal coverage report, and also
#report each new branch as it is discovered.
