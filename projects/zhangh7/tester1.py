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
count=0

visited = []
startTime=time.time()
elapsed=0

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

start=time.time()
while time.time()-start <= timeout:
	if isRandomTest:
		print "\n----------------------------Start random test-------------------------\n"
		isRandomTest=0
	sut.restart()
	depthNum=1
	for s1 in xrange(0,depth):
		if time.time()-start > timeout:
			break
		depthNum += 1
		startState=sut.state()
		action = sut.randomEnabled(rgen)
		ifRunning(running,action)
		
		ok = sut.safely(action)
		ss = sut.state()
		if ss not in visited:
			visited.append(ss)
		if not ok:
			print "FOUND A FAILURE"
			print sut.failure()
			print "REDUCING"
			R = sut.reduce(sut.test(),sut.fails, True, True)
			if R not in Rlist:
				sut.prettyPrintTest(R)
				f2_random = sut.failure()
				writeFaults(faults,0,R,f2_random,'faults1.test')
				print sut.failure()
				Rlist.append(R)
				
			expr = visited[-2]
			queue = [startState]
	
			d=1
			print '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~`Start BFS test~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
			while d<=dfsDepth and depthNum + dfsDepth<= depth and time.time()-start <= timeout:
				print "DEPTH",d,"QUEUE SIZE",len(queue),"VISITED SET",len(visited)
				d+=1
				depthNum += 1
				frontier = []
				for s2 in queue[:width]:
					if time.time()-start > timeout:
						break
					sut.backtrack(s2)
					allEnabled = sut.enabled()
					rgen.shuffle(allEnabled)
					for a in allEnabled:
						if time.time()-start > timeout:
							break
						ifRunning(running,a)
						ok = sut.safely(a)
						sss = sut.state()
						if  sss!=ss and sss!=expr:
							if sss not in visited:
								visited.append(sss)
								frontier.append(sss)
							if not ok:
								R = sut.reduce(sut.test(),sut.fails, True, True)
								if R not in Rlist:
									print "FOUND A FAILURE"
									print "REDUCING"
									f1_bfs=sut.prettyPrintTest(R)
									f2_bfs=sut.failure()
									writeFaults(faults,1,R,f2_bfs,'faults1.test')
									print sut.failure()
									Rlist.append(R)
									break
					else:			
						sut.backtrack(s2)
						continue
					break
				queue = frontier
			isRandomTest=1


print "\n Test Ended\n"
if coverage:
	sut.internalReport()
