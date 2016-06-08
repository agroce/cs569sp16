import sut
import random
import sys
import time
import os
import argparse as arg

parser = arg.ArgumentParser()
parser.add_argument('timeout', type=int, default=30, help='Maximum testing time.')
parser.add_argument('seed', type=int, nargs='?', default=7, help='Randomization seed.')
parser.add_argument('depth', type=int, nargs='?', default=100, help='Maximum length.')
parser.add_argument('width', type=int, nargs='?', default=10, help='Maximum memory/BFS queue/other parameter.')
parser.add_argument('fault', type=int, nargs='?', default=0, help='Whether the tester checks for faults.')
parser.add_argument('coverage', type=int, nargs='?', default=0, help='Whether a final coverage report produces.')
parser.add_argument('running', type=int, nargs='?', default=0, help='Whether running info on branch coverage should be produced.')
parser.add_argument('factor', type=float, nargs='?', default=1.0, help="Control how much test instances in active pool.")
parsed_args = parser.parse_args(sys.argv[1:])

def collectCoverage():
    global coverageCount
    for s in sut.currStatements():
        if s not in coverageCount:
            coverageCount[s] = 0
        coverageCount[s] += 1

def expandPool():
    global belowMean,lastAddCoverage
    if len(sut.newStatements()) != 0:
        print "NEW STATEMENTS DISCOVERED",sut.newStatements()
        oldTest = list(sut.test())

        storeTest = sut.reduce(oldTest,sut.coversStatements(sut.newStatements()))
        print "OLD LENGTH = ",len(oldTest),"NEW LENGTH = ",len(storeTest)
        sut.replay(oldTest)
        fullPool.append((storeTest, set(sut.currStatements())))
        lastAddCoverage = set(sut.currStatements())
        return
    for s in belowMean:
        if s in sut.currStatements() and s not in lastAddCoverage:
            print "NEW PATH TO LOW COVERAGE STATEMENT",s
            fullPool.append((list(sut.test()), set(sut.currStatements())))
            lastAddCoverage = set(sut.currStatements())
            return

def randomAction():
    global actCount, bugs, failPool, faults, start, failureFiles
    act = sut.randomEnabled(rgen)
    actCount += 1
    ok = sut.safely(act)
    elapsed = time.time() - start
    if running:
        if len(sut.newBranches()) > 0:
            print "ACTION:", act[0]
            for branch in sut.newBranches():
                print elapsed, len(sut.allBranches()), "New branch", branch

    if not ok:
        bugs += 1
        print "FOUND A FAILURE, REDUCING..."
        failPool.append(sut.test())
        collectCoverage()
        R = sut.reduce(sut.test(),sut.fails, True, True)

        if faults:
            print "SAVING INTO FILE NAMED failurefile"+str(bugs)
            failureFile = "failure" + str(bugs) + ".test"
            sut.saveTest(sut.test(), failureFile)
            failureFiles.append(failureFile)

        sut.restart()
    else:
        expandPool()
    return ok

def findBelowMean():
    global belowMean

    belowMean = set([])
    sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])

    coverSum = sum(coverageCount.values())
    if len(coverageCount) == 0:
        coverMean = coverSum
    else:
        coverMean = coverSum / (factor*len(coverageCount))  
    for s in sortedCov:
        if coverageCount[s] < coverMean:
            belowMean.add(s)
        else:
            break
    print len(belowMean),"STATEMENTS BELOW MEAN COVERAGE OUT OF",len(coverageCount)
    newBelowMean = set([])
    coverSum = sum(map(lambda x:coverageCount[x],belowMean))
    if len(coverageCount) == 0:
        coverMean = coverSum
    else:
        coverMean = coverSum / (factor*len(coverageCount))  
    for s in belowMean:
        if coverageCount[s] < coverMean:
            newBelowMean.add(s)
    print len(newBelowMean),"STATEMENTS BELOW MEAN COVERAGE OUT OF",len(belowMean)
    belowMean = newBelowMean

def printCoverage():
    sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])

    coverSum = sum(coverageCount.values())
    if len(coverageCount) == 0:
        coverMean = coverSum
    else:
        coverMean = coverSum / (factor*len(coverageCount))  
    print "MEAN COVERAGE IS",coverMean
    for s in sortedCov:
        print s, coverageCount[s]

def buildActivePool():
    global activePool
    findBelowMean()
    activePool = []
    for (t,c) in fullPool:
        for s in c:
            if s in belowMean:
                activePool.append((t,c))
                break
    print len(activePool),"TESTS IN THE ACTIVE POOL,",len(fullPool),"IN FULL POOL"        

def exploitPool():
    if activePool != []:
        sut.replay(rgen.choice(activePool)[0])
    else:
        sut.replay(rgen.choice(fullPool)[0])


BUDGET          = vars(parsed_args)['timeout']
SEED            = vars(parsed_args)['seed']
depth           = vars(parsed_args)['depth']
width           = vars(parsed_args)['width']
faults          = vars(parsed_args)['fault']
coverage_report = vars(parsed_args)['coverage']
running         = vars(parsed_args)['running']
factor          = vars(parsed_args)['factor']

if factor < 0.1:
    print "The factor you input is too small! Default value is 1.0"
    print "Please consider a float between 0.1 and 2.0"
    factor = 1.0
elif factor > 2.0:
    print "The factor you input is too big! Default value is 1.0"
    print "Please consider a float between 0.1 and 2.0"
    factor = 1.0

rgen = random.Random()
rgen.seed(SEED)

explore = 0.7

actCount = 0

sut = sut.sut()

bugs = 0

coverageCount = {}
activePool = []
fullPool = []
failPool = []
failureFiles = []

belowMean = set([])

print "STARTING PHASE 1"

start = time.time()
ntests = 0
while time.time()-start < BUDGET / 2:
    sut.restart()
    ntests += 1
    for w in xrange(0, width):
        if time.time() - start >= BUDGET / 2:
            break
        for s in xrange(0,depth):
            if time.time() - start >= BUDGET / 2 or not randomAction():
                break
    collectCoverage()

printCoverage()
print "STARTING PHASE 2"

start = time.time()
while time.time()-start < BUDGET / 2:
    buildActivePool()
    lastAddCoverage = set([])
    sut.restart()
    if rgen.random() > explore:
        exploitPool()
        lastAddCoverage = set(sut.currStatements())
    ntests += 1
    for w in xrange(0, width):
        if time.time() - start >= BUDGET / 2:
            break
        for s in xrange(0,depth):
            if time.time() - start >= BUDGET / 2 or not randomAction():
                break
    collectCoverage()

if coverage_report:
    sut.internalReport()
    sut.report("coverage_report.txt")
    if not os.path.isdir("html"):
        os.mkdir("html")

    sut.htmlReport("./html")


print ntests,"TESTS"


for (t,s) in fullPool:
    print len(t),len(s)

# collects all failed tests into one file named "failureCollection"
with open('failureCollection.out', 'w') as outfile:
    i = 1
    for fname in failureFiles:
        with open(fname) as infile:
            outfile.write("FOUND failure "+str(i)+"\n")
            for line in infile:
                outfile.write(line)
            outfile.write("\n")
            i += 1


print bugs,"FAILED"
print "TOTAL ACTIONS",actCount
print "TOTAL COVERED", len(sut.allBranches()), "BRANCHES"
print "TOTAL COVERED", len(sut.allStatements()), "STATEMENTS"
print "TOTAL RUNTIME",time.time()-start

