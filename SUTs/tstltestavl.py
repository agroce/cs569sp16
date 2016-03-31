import sut
import random
import sys

rgen = random.Random()

DEPTH = 100
NUM_TESTS = 1000

sut = sut.sut()

for t in xrange(0,NUM_TESTS):
    sut.restart()
    for s in xrange(0,DEPTH):
        action = sut.randomEnabled(rgen)
        ok = sut.safely(action)
        propok = sut.check()
        if ((not ok) or (not propok)):
            sut.prettyPrintTest(sut.test())
            R = sut.reduce(sut.test(), lambda x: sut.fails(x) or sut.failsCheck(x))
            print "TEST FAILED"
            sut.prettyPrintTest(R)
            sys.exit(1)

