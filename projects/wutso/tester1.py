import sut, random, sys, time

def notOK():
    global bugs, sut
    bugs += 1
    print "FOUND A FAILURE"
    print sut.failure()
    print "REDUCING"
    R = sut.reduce(sut.test(), sut.fails, True, True)
    sut.prettyPrintTest(R)
    print sut.failure()

def collectCoverage():
    global sut, coverageCount
    for s in sut.currStatements():
        if s not in coverageCount:
            coverageCount[s] = 0    
        coverageCount[s] += 1

def abstract(name):
    abs = ""
    for c in name:
        if c not in ['0','1','2','3','4','5','6','7','8','9']:
            abs += c
    return abs   

# main
rgen          = random.Random()
sut           = sut.sut()

BUDGET          = int(sys.argv[1]) # 30 
SEED            = int(sys.argv[2]) # 1
DEPTH           = int(sys.argv[3]) # 100
WIDTH           = int(sys.argv[4]) # 1
FAULT_CHECK     = int(sys.argv[5]) # 0
COVERAGE_REPORT = int(sys.argv[6]) # 1
RUNNING_DETAIL  = int(sys.argv[7]) # 1

bugs          = 0
actCount      = 0
explore       = 0.7
k             = 10
coverageCount = {}
actionCount   = {}
leastCovered  = None
savedTest     = None

# start
rgen.seed(SEED)
start = time.time()
while time.time() - start < BUDGET:
    
    sut.restart()
    if (savedTest != None) and (rgen.random() > explore):
        print "EXPLOITING"
        sut.backtrack(savedTest)
    
    storedTest = False    
    
    for s in xrange(0, DEPTH):
        act = sut.randomEnabled(rgen)

        if len(sut.newStatements()) > 0:
            savedTest  = sut.state()
            storedTest = True
            print "FOUND NEW STATEMENTS", sut.newStatements()

        if (not storedTest) and (leastCovered != None) and (leastCovered in sut.currStatements()):
            savedTest  = sut.state()
            storedTest = True
        

        # apply count taken
        for action in sut.actions():
            actionCount[abstract(action[0])] = 0

        acts     = sut.randomEnableds(rgen, k)
        sortActs = sorted(acts, key=lambda x:actionCount[abstract(x[0])])
        act      = sortActs[0]
        actCount += 1
        ok  = sut.safely(act)
        if not ok:
            notOK()
            break

        collectCoverage()

    sortedCov    = sorted(coverageCount.keys(), key = lambda x: coverageCount[x])
    leastCovered = sortedCov[0]
    print "LEAST COVERED STATEMENT IS",leastCovered,coverageCount[leastCovered]

sut.internalReport()

sortedCov = sorted(coverageCount.keys(), key = lambda x: coverageCount[x])
for s in sortedCov:
    print s, coverageCount[s] 

print bugs,"FAILED"
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time() - start
