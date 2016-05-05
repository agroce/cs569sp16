import sut
import random
import time

r = random.Random()

sut = sut.sut()

NTESTS = 100
LENGTH = 100

tests = []
states = []

for i in xrange(0,NTESTS):
    sut.restart()
    for s in xrange(0,LENGTH):
        sut.safely(sut.randomEnabled(r))
    tests.append(sut.test())
    states.append(sut.state())

start = time.time()
for t in tests:
    sut.replay(t)
elapsed = time.time()-start
print "TOTAL TIME TO REPLAY:",elapsed

start = time.time()
for s in states:
    sut.backtrack(s)
elapsed = time.time()-start
print "TOTAL TIME TO BACKTRACK:",elapsed
