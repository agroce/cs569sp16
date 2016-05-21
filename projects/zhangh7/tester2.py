import sut
import random
import sys
import time

sut=sut.sut()
#sut.silenceCoverage()

timeout = int(sys.argv[1])
seed = int(sys.argv[2])
depth = int(sys.argv[3])
width = int(sys.argv[4])
faults = int(sys.argv[5])
coverage = int(sys.argv[6])
running = int(sys.argv[7])

rgen = random.Random(seed)

isRandomTest = 1

Rlist=[]
dfsDepth=5
BfsBugCount=0

visited = []
startTime=time.time()
failureNum = 0
population = []
rtTimePara=2
bestNum=10
BfsBugNum=3
elapsed=0

############write faults to one single file fault1.test (reduce)
'''
def writeFaults(faults,phase,R,f2,name):
	global count 
	if faults:
		count+=1
		f_file = name
		f1=''
		for i in range(len(R)):
			f1=f1+R[i][0]+'\n'
		with open(f_file,'a') as f:
			if not phase:
				f.write('\nFaults found in random test phase:\n')
			else:
				f.write('\nFaults found in bfs test phase:\n')
			f.write('\n'+str(count)+':-------\n'+str(f1)+'\n')
			f.write(str(f2)+'\n')
'''

#################write faults to seperate file failure1.test failure2.test ..... (Not reduce)
def newWriteFaults(f1,f2,name):
	f_file = name
	with open(f_file,'a') as f:
		f.write(str(f1)+'\n')
		f.write(str(f2)+'\n')

def ifRunning(running,action):
	if running:
		if sut.newBranches() != set([]):
			print "ACTION:",action[0]
			for b in sut.newBranches():
				print elapsed,len(sut.allBranches()),"New branch",b
			sawNew = True
		else:
			sawNew = False
		if sut.newStatements() != set([]):
			print "ACTION:",action[0]
			for s in sut.newStatements():
				print elapsed,len(sut.allStatements()),"New statement",s
			sawNew = True
		else:
			sawNew = False

def mutate(test,failureNum,start,timeout,running):
	tcopy = list(test)
	i = rgen.randint(0,len(tcopy))
	sut.replay(tcopy[:i],catchUncaught = True)
	e = sut.randomEnabled(rgen)
	ok = sut.safely(e)
	ifRunning(running,e)
	if not ok:
		failureNum+=1
		print "FIND " + str(failureNum) + " FAILURE"
		#print sut.failure()
		##########call newWriteFaults(), Not reduce
		if faults:
			name='failure'+str(failureNum)+'.test'
			f1_mutate = sut.test()
			f2_mutate = sut.failure()
			newWriteFaults(f1_mutate,f2_mutate,name)
		##########
	trest = [e]
	for s in tcopy[i+1:]:
		if time.time()-start > timeout:
			break
		if s[1]():
			trest.append(s)
			ok=sut.safely(s)
			ifRunning(running,s)
			if not ok:
				failureNum+=1
				print "FIND " + str(failureNum) + " FAILURE"
				#print sut.failure()
				##########call newWriteFaults(), Not reduce
				if faults:
					name='failure'+str(failureNum)+'.test'
					f1_mutate = sut.test()
					f2_mutate = sut.failure()
					newWriteFaults(f1_mutate,f2_mutate,name)
				##########
	tcopy = test[:i]+trest
	return tcopy,failureNum

start=time.time()
while time.time()-start <= timeout/rtTimePara:
	if isRandomTest:
		#print "\n----------------------------Start random test-------------------------\n"
		isRandomTest=0
	sut.restart()
	depthNum=1
	for s1 in xrange(0,depth):
		if time.time()-start > timeout/rtTimePara:
			break
		depthNum += 1
		#startState=sut.state()
		action = sut.randomEnabled(rgen)
		ok = sut.safely(action)
		ifRunning(running,action)
		ss = sut.state()
		if ss not in visited:
			visited.append(ss)
		if not ok:
			currentTest=list(sut.test())
			failureNum+=1
			print "FIND " + str(failureNum) + " FAILURE"
			#print sut.failure()
			
			##########call newWriteFaults(), Not reduce
			if faults:
				name='failure'+str(failureNum)+'.test'
				f1_random = sut.test()
				f2_random = sut.failure()
				newWriteFaults(f1_random,f2_random,name)
			##########
			'''
			############## call writeFaults()
			print "REDUCING"
			R = sut.reduce(sut.test(),sut.fails, True, True)
			if R not in Rlist:
				sut.prettyPrintTest(R)
				f2_random = sut.failure()
				writeFaults(faults,0,R,f2_random,'faults1.test')
				print sut.failure()
				Rlist.append(R)
			'''
			
			sut.replay(currentTest,catchUncaught = True)
			expr = sut.state()
			queue = [expr]
	
			d=1
			#print '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~`Start BFS test~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
			while depthNum + d <= depth and time.time()-start <= timeout/rtTimePara:
				#print "DEPTH",depthNum + d,"QUEUE SIZE",len(queue),"VISITED SET",len(visited)
				d+=1
				#depthNum += 1
				frontier = []
				for s2 in queue[:width]:
					if time.time()-start > timeout/rtTimePara:
						break
					sut.backtrack(s2)
					allEnabled = sut.enabled()
					rgen.shuffle(allEnabled)
					for a in allEnabled[:5]:
						if time.time()-start > timeout/rtTimePara:
							break
						ok = sut.safely(a)
						ifRunning(running,a)
						sss = sut.state()
						if  sss!=ss and sss!=expr:
							if sss not in visited:
								visited.append(sss)
								frontier.append(sss)
							if not ok:
								failureNum+=1
								print "FIND " + str(failureNum) + " FAILURE"
								#print sut.failure()
								##########Not reduce
								if faults:
									name='failure'+str(failureNum)+'.test'
									f1_bfs = sut.test()
									f2_bfs = sut.failure()
									newWriteFaults(f1_bfs,f2_bfs,name)
								##########
								'''
								############## call writeFaults()
								R = sut.reduce(sut.test(),sut.fails, True, True)
								if R not in Rlist:
									print "FOUND A FAILURE"
									print "REDUCING"
									f1_bfs=sut.prettyPrintTest(R)
									f2_bfs=sut.failure()
									writeFaults(faults,1,R,f2_bfs,'faults1.test')
									print sut.failure()
									Rlist.append(R)
								'''
								BfsBugCount+=1
								if BfsBugCount==BfsBugNum:
									BfsBugCount=0
									break
					else:			
						sut.backtrack(s2)
						continue
					break
				rgen.shuffle(frontier)
				queue = frontier
			isRandomTest=1
	population.append((list(sut.test()),set(sut.currBranches())))
	
#print "STARTING POP BRANCHCOV",len(sut.allBranches()) 
#print "STARTING POP STATEMENTCOV",len(sut.allStatements())

#print "\n----------------------------Start mutate test-------------------------\n"

while time.time()-start < timeout:
	sortPop = sorted(population,key = lambda x: len(x[1]),reverse=True)
	(t,b) = rgen.choice(sortPop[:bestNum])
	m,failureNum = mutate(t,failureNum,start,timeout,running)
	population.append((m,sut.currBranches()))

print "TOTAL TESTING TIME:",time.time()-start

print "\n Test Ended\n"
if coverage:
	sut.internalReport()