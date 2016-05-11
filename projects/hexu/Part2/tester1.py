import sys
import random
import sut
import time

Timeout  = int(sys.argv[1])
Seed 	 = int(sys.argv[2])
Depth 	 = int(sys.argv[3])
Width  	 = int(sys.argv[4])
Faults   = int(sys.argv[5])
Coverage = int(sys.argv[6])
Running  = int(sys.argv[7])

rgen = random.Random(Seed)

sut = sut.sut()

start = time.time()

bugs = 0

acts = 0

for m in xrange(0,Width):
	if time.time() - start > Timeout:
		break
	sut.restart()
	for t in xrange(0,Depth):
		if time.time() - start > Timeout:
			break
		act = sut.randomEnabled(rgen)
		ok  = sut.safely(act)
		acts += 1
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
			sut.restart()
		if Running :
			if sut.newBranches() != set([]):
				print "ACTION:", act[0]
				elapsed = time.time() - start
				for b in sut.newBranches():
					print elapsed,len(sut.allBranches()),"New branch",b
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
