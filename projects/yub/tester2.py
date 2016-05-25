import sut
import random
import sys
import time

timeout = int(sys.argv[1])
seed = int(sys.argv[2])
depth = int(sys.argv[3])
width = int(sys.argv[3])
faults = int(sys.argv[4])
coverage = int(sys.argv[5])
running = int(sys.argv[6])


rgen = random.Random()
sut = sut.sut()
actNum = 0
bugs = 0
weight = 0
exp = 0.4
lenth = 100
test = None
lCovered = None
coverageNum = {}
coverageWBM = []
start = time.time()
def tester():
    global sut,act,n,test,para,lCovered,actNum,bugs,M,flag, filename
    act = sut.randomEnabled(rgen)
    flag = 0
    n = sut.safely(act)
    if running:
        if sut.newBranches() != set([]):
            for d in sut.newBranches():
                print time.time() - start, len(sut.allBranches()),"New branch",d
    if len(sut.newStatements()) > 0:
        test = sut.state()
        para = True
        print sut.newStatements()
    if (para == False):
        if (lCovered != None):
            if (lCovered in sut.currStatements()):
                test = sut.state()
                para = True
    actNum += 1
    if (n == 0):
        bugs += 1
        print "A failure has been found!", bugs
        print sut.failure()
        M = sut.reduce(sut.test(),sut.fails, True, True)
        sut.prettyPrintTest(M)
        print sut.failure()
        filename ='failure%d.test'%bugs
        sut.saveTest(M,filename)
        flag = 1
    

def main():
    global flag,timeout,sut,test,para,currStatements,coverageNum,sortedCov,weight,weightedCov,coverageWBM,bugs,actNum,start
    while time.time()-start < timeout:
        sut.restart()
        if (test != None):
            if (rgen.random() > exp):
                sut.backtrack(test)
        para = False
        for s in xrange(0,lenth):
            tester()
            if flag == 1:
                break
        for s in sut.currStatements():
            if s not in coverageNum:
                coverageNum[s] = 0
            coverageNum[s] += 1
        sortedCov = sorted(coverageNum.keys(), key=lambda x: coverageNum[x])
        for c in sortedCov:
            weightedCov = c * (lenth - coverageNum[c])
            if weightedCov > 20:
                coverageWBM.append(weightedCov)
                print c
    sut.internalReport()
    for s in sortedCov:
        print s, coverageNum[s]


    print bugs,"Failures have been found"
    print "TOTAL ACTIONS",actNum
    print "TOTAL RUNTIME",time.time()-start
if __name__ == '__main__':
    main()