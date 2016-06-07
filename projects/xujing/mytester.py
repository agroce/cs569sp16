import sut
import sys
import random
import time
import os
import math
import traceback

timeout = int(sys.argv[1])
seed = int(sys.argv[2])
depth = int(sys.argv[3])
width = int(sys.argv[4])
faults = int(sys.argv[5])
coverage = int(sys.argv[6])
running = int(sys.argv[7])
quickTests= int(sys.argv[8])
outputfile="outputest.out"

def randomAction():
    global actCount, bugs,newseq,currseq
    act = sut.randomEnabled(R)
    actCount += 1
    ok = sut.safely(act)

    if running:
        if len(sut.newBranches()) > 0:
            print "ACTION:",act[0]
            for b in sut.newBranches():
                print time.time() - start, len(sut.allBranches()),"new branch",b
            for s1 in sut.newStatements():
                print time.time() - start, len(sut.allStatements()),"new statement",s1

    if not ok:
        bugs += 1
        print "FOUND A FAILURE"

        if faults:
            f = sut.reduce(sut.test(), sut.fails, True, True)
            sut.prettyPrintTest(f)
            currseq.append((f,set(sut.currStatements())))
            print("SHOW FAULT")
            file = 'failure' + str(actCount) + '.test'
            sut.saveTest(sut.test(), file)
            sut.restart()
            print sut.failure()


    return ok

def flags(newseq,c):
    pass


def checkAlg():
    global error, noerror,newseq,currseq,states
     #newseq = sut.randomEnableds(R, depth)
    newseq=sut.newStatements()
    c = sut.check()
    if c:
        if(not ((newseq in error) or (newseq in noerror))):
            states.insert(ntest-1,sut.state())
            noerror.append(sut.currStatements())
            flags(newseq,c)
    else:
        error.append(sut.currStatements())

    #if not error ==[]:
    #    print "SHOW ERROR SEQUENCE"
        #    print error
        #f = open(("failure" + str(actCount) + ".test"), 'w')
        #f.write(str(error))
        #f.close()
    #else:
    #    print "Data in noerror sequence"
        # print noerror

def handle_failure(test, msg, checkFail, newCov = False):
    global failCount, reduceTime, repeatCount, failures, quickCount, failCloud, cloudFailures, allClouds, localizeSFail, localizeBFail
    test = list(test)
    sys.stdout.flush()
    if not newCov:
        failCount += 1
        print msg
        f = sut.failure()
        print "ERROR:",f
        print "TRACEBACK:"
        traceback.print_tb(f[2])
        sut.saveTest(test,outputfile+".full")
    else:
        print "Handling new coverage for quick testing"
        snew = sut.newCurrStatements()
        for s in snew:
            print "NEW STATEMENT",s
        bnew = sut.newCurrBranches()
        for b in bnew:
            print "NEW BRANCH",b
        trep = sut.replay(test)
        sremove = []
        scov = sut.currStatements()
        for s in snew:
            if s not in scov:
                print "REMOVING",s
                sremove.append(s)
        for s in sremove:
            snew.remove(s)
        bremove = []
        bcov = sut.currBranches()
        for b in bnew:
            if b not in bcov:
                print "REMOVING",b
                bremove.append(b)
        for b in bremove:
            bnew.remove(b)
        beforeReduceS = set(sut.allStatements())
        beforeReduceB = set(sut.allBranches())
    print "Original test has",len(test),"steps"
    cloudMatch = False

    if newCov:
        failProp = sut.coversAll(snew,bnew)
    print "REDUCING..."
    startReduce = time.time()
    original = test
    #test = sut.reduce(test, failProp, True, config.keep)
    if not newCov:
        sut.saveTest(test,outputfile+".reduced")
    print "Reduced test has",len(test),"steps"
    print "REDUCED IN",time.time()-startReduce,"SECONDS"
    sut.prettyPrintTest(test)

    i = 0
    outf = None
    if quickTests==1:
        outname = outputfile
        if (outname != None)  and not newCov:
            outname += ("." + str(failCount))
        if quickTests==1 and newCov:
            for s in sut.allStatements():
                if s not in beforeReduceS:
                    print "NEW STATEMENT FROM REDUCTION",s
            for b in sut.allBranches():
                if b not in beforeReduceB:
                    print "NEW BRANCH FROM REDUCTION",b
            outname = "quicktest." + str(quickCount)
            quickCount += 1
        if outname != None:
            outf = open(outname,'w')

    print "FINAL VERSION OF TEST:"
    i = 0
    sut.restart()
    for s in test:
        steps = "# STEP " + str(i)
        print sut.prettyName(s[0]).ljust(80-len(steps),' '),steps
        sut.safely(s)
        if checkFail:
            sut.check()
        i += 1
        if outf != None:
            outf.write(sut.serializable(s)+"\n")
    if not newCov:
        f = sut.failure()
        if f != None:
            print "ERROR:",f
            print "TRACEBACK:"
            traceback.print_tb(f[2])
        else:
            print "NO FAILURE!"
    sys.stdout.flush()
    if outf != None:
        outf.close()

def main():
    global start,sut,R,noerror,error,reduceTime,actCount, bugs,ntest,newseq,currseq,states, beforeReduceS, beforeReduceB,quickCount
    actCount = 0
    bugs = 0
    start = time.time()
    noerror = []
    error = []
    newseq = []
    ntest=0
    currseq=[]
    sut = sut.sut()
    reduceTime = 0.0
    R = random.Random()
    R.seed(seed)
    beforeReduceS = set(sut.allStatements())
    beforeReduceB = set(sut.allBranches())
    states = [sut.state()]
    quickCount=0
    print "STARTING PHASE 1"
    while(time.time() < start + timeout):
        for st in states:
            ntest+=1
            if (time.time() > start + timeout):
                break
            sut.restart()
            sut.backtrack(st)
            for s in xrange(0, depth):
                if (time.time() > start + timeout):
                    break
                ok = randomAction()
                if not ok:
                    break
                checkAlg()

    if coverage:
        sut.internalReport()
    if quickTests==1:
        #if (sut.newCurrBranches() != set([])) or (sut.newCurrStatements() != set([])):
        handle_failure(sut.test(), "NEW COVERAGE", False, newCov=True)


    print "TOTAL BUGS", bugs
    print "TOTAL ACTIONS",actCount
    print "TOTAL RUNTIME",time.time()-start

if __name__ == '__main__':
    main()

