import sut
import random
import sys
import time
import argparse
from collections import namedtuple

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--depth', type=int, default=100,help='Maximum search depth (100 default).')
	parser.add_argument('-t', '--timeout', type=int, default=60,help='Timeout in seconds (60 default).')
	parser.add_argument('-s', '--seed', type=int, default=None,help='Random seed (default = None).')
	parser.add_argument('-R', '--reduce', action='store_true',help="Reduce -- report reduced failing test.")
	parser.add_argument('-f', '--faults', action='store_true',help="save a test case for each discovered failure.")
	parser.add_argument('-N', '--normalize', action='store_true',help="Normalize/simplify after reduction.")
	parser.add_argument('-w', '--width', type=int, default=5,help="maximum memory/BFS queue/other parameter that is basically a search width.") 
	parser.add_argument('-r', '--running', action='store_true',help="Produce running branch coverage report.")
	parser.add_argument('-c', '--coverage', action='store_true',help="Produce a coverage report at the end.")
	parser.add_argument('-b', '--bfs', action='store_true',help="Using BFS when find new statements or branches")
	parser.add_argument('-m', '--ifmutate', action='store_true',help="Using genetic testing when coverage does not change for a setting time")
	parser.add_argument('-a', '--auto', action='store_true',help="According to input timeout, choosing test strategy by tester itself")
	parser.add_argument('-T', '--TargetOnBug', action='store_true',help="This mode target on finding bugs")
	parsed_args = parser.parse_args(sys.argv[1:])
	return (parsed_args, parser)

def make_config(pargs, parser):
	pdict = pargs.__dict__
	key_list = pdict.keys()
	arg_list = [pdict[k] for k in key_list]
	Config = namedtuple('Config', key_list)
	nt_config = Config(*arg_list)
	return nt_config   

def ifRunning(elapsed,running,action):
	sawNewBran=False
	sawNewStat=False
	if sut.newBranches() != set([]):
		if running:
			print "ACTION:",action[0]
			for b in sut.newBranches():
				print elapsed,len(sut.allBranches()),"New branch",b
		sawNewBran = True
	else:
		sawNewBran = False
	if sut.newStatements() != set([]):
		if running:
			print "ACTION:",action[0]		
			for s in sut.newStatements():
				print elapsed,len(sut.allStatements()),"New statement",s
		sawNewStat = True
	else:
		sawNewStat = False
	return sawNewBran,sawNewStat

def Failure(failureNum,f):
	failureNum+=1
	#print "FIND " + str(failureNum) + " FAILURE"
	if faults:
		name='failure'+str(failureNum)+'.test'
		sut.saveTest(f,name)
	if reduce:
		print "REDUCING"
		R = sut.reduce(sut.test(),sut.fails, True, True)
		sut.prettyPrintTest(R)
		if normalize:
			print "NOMALIZING"
			N = sut.normalize(R,sut.fails, True, True)
			sut.prettyPrintTest(N)
	return failureNum

def BFS(state,failureNum,depthNum,lastCovTime,newCovTime):
	queue = [state]
	d=0
	BfsBugCount=0
	newCovBran=False
	newCovStat=False
	while depthNum + d < depth and time.time()-start <= timeout/rtTimePara and (newCovBran==False and newCovStat==False):
		d+=1
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
				newCovBran, newCovStat = ifRunning((time.time()-start),running,a)
				sss = sut.state()
				if sss not in visited:
					visited.append(sss)
					frontier.append(sss)
				if not ok:
					f1_bfs = sut.test()
					failureNum = Failure(failureNum,f1_bfs)
					BfsBugCount+=1
					if BfsBugCount==BfsBugNum:
						BfsBugCount=0
						break
				if newCovBran or newCovStat:
					lastCovTime = time.time()
					newCovTime = 0
					break
				else:
					newCovTime = time.time() - lastCovTime
				sut.backtrack(s2)
			else:
				sut.backtrack(s2)
				continue
			break
		rgen.shuffle(frontier)
		queue = frontier
	return failureNum

def mutate(test,failureNum,start,timeout,running):
	tcopy = list(test)
	i = rgen.randint(0,len(tcopy))
	sut.replay(tcopy[:i],catchUncaught = True)
	e = sut.randomEnabled(rgen)
	ok = sut.safely(e)
	ifRunning((time.time()-start),running,e)
	if not ok:
		f1_mutate = sut.test()
		failureNum = Failure(failureNum,f1_mutate)
	trest = [e]
	for s in tcopy[i+1:]:
		if time.time()-start > timeout:
			break
		if s[1]():
			trest.append(s)
			ok=sut.safely(s)
			newCovBran, newCovStat = ifRunning((time.time()-start),running,action)
			if not ok:
				f1_mutate = sut.test()
				failureNum = Failure(failureNum,f1_mutate)
				if bug:
					BFSstartState = sut.state()
					failureNum = BFS(BFSstartState,failureNum,depthNum,lastCovTime,newCovTime)
					break
			if bfs and (newCovBran or newCovStat):
				BFSstartState = sut.state()
				failureNum = BFS(BFSstartState,failureNum,depthNum,lastCovTime,newCovTime)
				break
	tcopy = test[:i]+trest
	return tcopy,failureNum

parsed_args, parser = parse_args()
config = make_config(parsed_args, parser)
print('Tester using config={}'.format(config))

timeout = config.timeout
rgen = random.Random(config.seed)
depth = config.depth
width = config.width
faults = config.faults
coverage = config.coverage
running = config.running
reduce = config.reduce
normalize = config.normalize
bfs = config.bfs
ifmutate = config.ifmutate
auto = config.auto
bug = config.TargetOnBug

sut=sut.sut()
#sut.silenceCoverage()

visited = []
startTime=time.time()
failureNum=0
population = []
rtTimePara=1
bestNum=10
BfsBugNum=3
elapsed=0
newCovTime=0
lastCovTime=0

start=time.time()
newCovTime = time.time()-start
lastCovTime = time.time()

if ifmutate:
	rtTimePara=2

if auto:
	if timeout < 30:
		rtTimePara = 1
		bfs = False

while time.time()-start <= timeout/rtTimePara:
	if ifmutate:
		if newCovTime > max(6,timeout/10):
			break
	sut.restart()
	depthNum=0
	for s1 in xrange(0,depth):
		if time.time()-start > timeout/rtTimePara:
			break
		depthNum += 1
		#startState=sut.state()
		action = sut.randomEnabled(rgen)
		ok = sut.safely(action)
		newCovBran, newCovStat = ifRunning((time.time()-start),running,action)
		if newCovBran or newCovStat:
			lastCovTime = time.time()
			newCovTime = 0
		else:
			newCovTime = time.time() - lastCovTime
		ss = sut.state()
		if ss not in visited:
			visited.append(ss)
		if not ok:
			f1_random = sut.test()
			failureNum = Failure(failureNum,f1_random)
			if bug:
				BFSstartState = sut.state()
				failureNum = BFS(BFSstartState,failureNum,depthNum,lastCovTime,newCovTime)
				break
		if bfs and (newCovBran or newCovStat) and lastCovTime > max(2,timeout/100):
			BFSstartState = sut.state()
			failureNum = BFS(BFSstartState,failureNum,depthNum,lastCovTime,newCovTime)
			break
	population.append((list(sut.test()),set(sut.currBranches())))

while time.time()-start < timeout:
	sortPop = sorted(population,key = lambda x: len(x[1]),reverse=True)
	(t,b) = rgen.choice(sortPop[:bestNum])
	m,failureNum = mutate(t,failureNum,start,timeout,running)
	population.append((m,sut.currBranches()))

print "TOTAL TESTING TIME:",time.time()-start

print "\n Test Ended\n"
if coverage:
	sut.internalReport()