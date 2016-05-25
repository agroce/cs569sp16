#!/usr/bin/python
import random
import time
import math
import os
import sys
import sut
#implementing outliers of least coverages
# parsing parameters

rgen = random.Random()
def mutate(test):
    tcopy = list(test)
    i = rgen.randint(0,len(tcopy))
#    sut.replay(tcopy[:i])
    e = sut.randomEnabled(rgen)
    sut.safely(e)
    trest = [e]
    for s in tcopy[i+1:]:
        if s[1]():
            trest.append(s)
            sut.safely(s)
    tcopy = test[:i]+trest
    if len(sut.newCurrBranches()) != 0:
        print "NEW BRANCHES DUE TO MUTATION:",sut.newCurrBranches()
    return tcopy

TIME_OUT = int(sys.argv[1])

SEED = int(sys.argv[2])

DEPTH = int(sys.argv[3])

WIDTH = int(sys.argv[4])

FAULT = int(sys.argv[5])

COVERAGE= int(sys.argv[6])

RUNNING= int(sys.argv[7])

sut = sut.sut();

sut.silenceCoverage()
rand = random.Random()

savedTest = None


actCount = 0

bugs = 0

act = sut.randomEnabled(rgen)
tests = []
start = time.time()
population = []

print "STARTING POP BRANCHCOV",len(sut.allBranches())
print "STARTING POP STATEMENTCOV",len(sut.allStatements())
#tryStutter = (act != None) and (act[1]())
storedTest = False;
while(time.time()< start + TIME_OUT):
        for ts in xrange(0,WIDTH):
            sut.restart()
            for b in xrange(0,DEPTH):
                act = sut.randomEnabled(rgen)
                ok = sut.safely(act)
                new = False
                actCount += 1
                propok = sut.check()
               
                #if running=1, print elapsed time, total brach count, new branch otherwise don't print
                if RUNNING:
                    if sut.newBranches() != set([]):
                        print "Entered here"
#                        print "ACTION:",a[0],tryStutter
                        for b in sut.newBranches():
                            print time.time()-start,len(sut.allBranches())," branch",b
                        new = True
                    else:
                        new = False  
                if FAULT:
                        bugs += 1
                        fault = sut.failure();
                        fname = 'fault'+str(bugs)+'.test'
                        wfile = open(fname,'w')
                        wfile.write(str(fault))
                        wfile.close()
                        sut.restart()
                else:
                    if len(sut.newBranches()) != 0:
                        test = sut.test()
                        mut = mutate(test)
                        print "NEW BRANCHES FOUND",sut.newBranches()
                        tests.append((list(sut.test()), set(sut.currBranches()))) 
                        
                        population.append((mut,sut.currBranches()))

if COVERAGE:
    sut.internalReport()
print "Total Number of bugs",bugs
print "Total number of actions",actCount
print "Total Runtime",time.time()-start
print "FINAL POP BRANCHCOV",len(sut.allBranches())
print "FINAL POP STATEMENTCOV",len(sut.allStatements())    
