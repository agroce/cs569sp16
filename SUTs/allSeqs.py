import sut
import random
import sys
import time
from functools import partial

def addsSeq(action, seqLen=2):
    global seqs, sut, currSeq

    if "--random" in sys.argv:
        return True
    
    aord = str(sut.actOrder(action))
    newSeq = "." + aord + currSeq
    return newSeq not in seqs[seqLen]

rgen = random.Random()
depth = 100
maxSeqLen = int(sys.argv[1])

actCount = 0

BUDGET = 300.0

sut = sut.sut()
k = len(sut.actions())

minSeqLen = 3

seqs = {}
fails = {}
tries = {}
for i in xrange(2,maxSeqLen+1):
    seqs[i] = {}
    fails[i] = 0.0
    tries[i] = 0.0
    
numNew = 0

bugs = 0

everSkip = not ("--stubborn" in sys.argv)

start = time.time()
while time.time()-start < BUDGET:
    sut.restart()
    for s in xrange(0,depth):
        #print "DEPTH",s,map(sut.actOrder,sut.test())
        act = None
        if len(sut.test()) >= 1:
            suffix = []
            for slen in xrange(2,min(len(sut.test())+1,maxSeqLen)+1):
                suffix.append(sut.test()[-(slen-1)])
                if slen < minSeqLen:
                    continue
                if everSkip and fails[slen] > 0:
                    if rgen.random() < fails[slen]/tries[slen]:
                        #print "SKIPPING TRY AT LENGTH",slen, fails[slen]/tries[slen]
                        continue
                tries[slen] += 1
                currSeq = reduce(lambda x,y: x + "." + str(sut.actOrder(y)), suffix, "")
                act = sut.randomEnabledPred(rgen,k,partial(addsSeq, seqLen=slen))
                if addsSeq(act,seqLen=slen):
                    #print "FOUND NEW SEQUENCE OF LENGTH",slen,"."+str(sut.actOrder(act)) + currSeq
                    break
                else:
                    #print "FAILED TO FIND SEQUENCE OF LENGTH",slen
                    fails[slen] += 1.0
                    act = None
        if act == None:
            act = sut.randomEnabled(rgen)

        ok = sut.safely(act)            
        if len(sut.test()) > 1:
            suffix = [sut.test()[-1]]
            for slen in xrange(2,min(len(sut.test()),maxSeqLen)+1):
                suffix.append(sut.test()[-slen])
                currSeq = reduce(lambda x,y: x + "." + str(sut.actOrder(y)), suffix, "")
                #print "ADDING",slen,currSeq,len(seqs[slen])
                seqs[slen][currSeq] = True

        actCount += 1
        if not ok:
            bugs += 1
            print "FOUND A FAILURE"
            #sut.prettyPrintTest(sut.test())
            print sut.failure()
            print "REDUCING"
            R = sut.reduce(sut.test(),sut.fails, True, True)
            sut.prettyPrintTest(R)
            print sut.failure()
            sut.restart()                    

sut.internalReport()

for i in xrange(2,maxSeqLen+1):
    print "SEQS:",i,len(seqs[i]),fails[i],tries[i]

print bugs,"FAILED"
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-start
