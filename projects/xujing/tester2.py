import sut
import sys
import random
import time

timeout = int(sys.argv[1])
seed = int(sys.argv[2])
depth = int(sys.argv[3])
width = int(sys.argv[4])
faults = int(sys.argv[5])
coverage = int(sys.argv[6])
running = int(sys.argv[7])


def randomAction():
    global actCount, bugs
    act = sut.randomEnabled(R)
    actCount += 1
    ok = sut.safely(act)

    if running:
        if len(sut.newBranches()) > 0:
            print "ACTION:",sut.randomEnabled(random.Random(seed))[0]
            for b in sut.newBranches():
                print time.time() - start, len(sut.allBranches()),"New branch",b
            for s1 in sut.newStatements():
                print time.time() - start, len(sut.allStatements()),"New statement",s1

    if not ok:
        bugs += 1
        print "FOUND A FAILURE"
        error.append(sut.currStatements())
        if faults:
            print("SHOW FAULT")
            f = sut.reduce(sut.test(), sut.fails, True, True)
            sut.prettyPrintTest(f)
            print sut.failure()

    return ok


def main():
    global start,sut,R,noerror,error,actCount, bugs
    actCount = 0
    bugs = 0
    start = time.time()
    noerror = []
    error = []
    newseq = []
    belowMean = set([])
    ntest = 0
    coverageCount = {}
    sut = sut.sut()
    R = random.Random(seed)
    states = [sut.state()]
    print "STARTING PHASE 1"
    while(time.time() < start + timeout):
        for st in states:
            ntest += 1
            if (time.time() > start + timeout):
                break
            sut.restart()
            sut.backtrack(st)
            for s in xrange(0, depth):
                if (time.time() > start + timeout):
                    break
                newseq = sut.newStatements()
                ok = randomAction()
                if not ok:
                    break
                if(not ((newseq in error) or (newseq in noerror))):
                    states.insert(ntest-1,sut.state())
                    noerror.append(sut.currStatements())


    if not error ==[]:
        print "SHOW ERROR SEQUENCE"
        #    print error
        f = open(("error" + str(actCount) + ".out"), 'w')
        f.write(str(error))
        f.close()
    else:
        print "Data in noerror sequence"

    if coverage:
        sut.internalReport()


    print "TOTAL ACTIONS",actCount
    print "TOTAL RUNTIME",time.time()-start

if __name__ == '__main__':
    main()

