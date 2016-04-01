import sut
import random
import sys

rgen = random.Random()

DEPTH = 100
NUM_TESTS = 100

sut = sut.sut()
#sut.silenceCoverage()

for t in xrange(0,NUM_TESTS):
    sut.restart()
    for s in xrange(0,DEPTH):
        action = sut.randomEnabled(rgen)
        ok = sut.safely(action)
        propok = sut.check()
        if ((not ok) or (not propok)):
            #sut.prettyPrintTest(sut.test())
            print "TEST FAILED"
            print "REDUCING..."
            R = sut.reduce(sut.test(), lambda x: sut.fails(x) or sut.failsCheck(x))
            sut.prettyPrintTest(R)
            print "NORMALIZING..."
            N = sut.normalize(R, lambda x: sut.fails(x) or sut.failsCheck(x))
            #sut.prettyPrintTest(N)
            sut.generalize(N, lambda x: sut.fails(x) or sut.failsCheck(x))
            sys.exit(1)

sut.internalReport()

