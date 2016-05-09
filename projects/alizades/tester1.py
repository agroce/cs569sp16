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
i = 0 

act = sut.randomEnabled(rgen)

start = time.time()

#tryStutter = (act != None) and (act[1]())
storedTest = False;
while(time.time()< start + TIME_OUT):
        for ts in xrange(0,WIDTH):
            sut.restart()
            for b in xrange(0,DEPTH):
                ok = sut.safely(act)
                new = False
                actCount += 1
                propok = sut.check()
               
                #if running=1, print elapsed time, total brach count, new branch otherwise don't print
                if RUNNING:
                    if sut.newBranches() != set([]):
#                        print "ACTION:",a[0],tryStutter
                        for b in sut.newBranches():
                            print time.time()-start,len(sut.allBranches())," branch",b
                        new = True
                    else:
                        new = False  
if (COVERAGE_REPORT):
    sut.internalReport()
    print "TOTAL NUMBER OF BUGS",bugs
