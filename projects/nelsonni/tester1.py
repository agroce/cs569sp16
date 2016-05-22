#!/usr/bin/python

import sut
import random
import sys
import time
import math
import bisect
from optparse import OptionParser

def main(argv):
    global sut, rgen, ntest, nbug, coverageCount, start, selectStatements, threshold
    parse_options(argv)

    # GLOBAL VARIABLES
    sut = sut.sut()
    rgen = random.Random(opts.seed)
    ntest = 0
    nbug = 0
    coverageCount = {}
    selectStatements = {}
    threshold = 0
    start = time.time()
    
    # PHASES
    phaseLimit = 0
    if opts.timeout < 30:
        phaseLimit = int(round(opts.timeout/3*2))
    else: 
        phaseLimit = int(round(opts.timeout/10))

    while (time.time() - start) < (0.95 * opts.timeout):
        randomPool = phase1(phaseLimit)
        selectPool = filterPool(randomPool)
        phase2(randomPool, selectPool)
        print "FULL POOL:",len(randomPool),", SELECT POOL:",len(selectPool)

    print "EXECUTED:",ntest,"tests"
    print "BUGS:",nbug
    print "TOTAL ELAPSED:",round(time.time() - start,5),"seconds"

    if (opts.coverage):
        sut.internalReport()

def phase1(timeLimit):
    global ntest
    BUDGET = timeLimit
    DEPTH = opts.depth
    print "-------------------------------------------"
    print "PHASE 1: Starting\t(BUDGET:",BUDGET,"seconds,","DEPTH:",DEPTH,"tests)"
    phase_start = time.time()
    phase_test = ntest

    pool = Pool("randomPool")
    
    elapsed = time.time()-phase_start
    while elapsed < BUDGET and (time.time() - start) < opts.timeout:
        sut.restart()
        ntest += 1
        if opts.progress and ntest % 300:
            update_progress(elapsed/BUDGET)
        for s in xrange(0,DEPTH):
            if not randomAction(pool):
                break
        collectCoverage() # collecting coverage at the end of each test
        elapsed = time.time()-phase_start
    if opts.progress:
        update_progress(1.0)
    
    interval = time.time()-phase_start
    print "PHASE 1: Ending\t\t(EXECUTED:",(ntest - phase_test),"tests, USED:",round(interval,5),"seconds)"
    print "-------------------------------------------"
    return pool

def phase2(randomPool, selectPool):
    global ntest
    DEPTH = opts.depth
    print "PHASE 2: Starting\t(FILTER SET:", len(selectStatements),"DEPTH:",DEPTH,"tests)"
    phase_start = time.time()
    phase_test = ntest

    mean = calculateMean(selectStatements)
    initialMean = mean

    while mean < threshold and (time.time() - start) < opts.timeout:
        sut.restart()
        test = selectPool.getRandom()
        #sut.replay(test[0])
        sut.backtrack(test[1])
        ntest += 1
        if opts.progress and ntest % 10:
            update_progress((mean - initialMean)/threshold)
        for s in xrange(0,DEPTH):
            if not randomAction(selectPool):
                break
        mean = calculateMean(selectStatements)
        collectCoverage() # collecting coverage at the end of each test
    if opts.progress:
        update_progress(1.0)
    
    interval = time.time()-phase_start
    print "PHASE 2: Ending\t\t(EXECUTED:",(ntest - phase_test),"tests, USED:",round(interval,5),"seconds)"
    print "-------------------------------------------"

def filterPool(pool):
    'Build a new pool from pool using coverage-based threshold'
    calculateBelowSet()
    pool.setFilter(selectStatements)
    filteredStatements = pool.runFilter()
    filteredPool = Pool("selectPool",filteredStatements)
    return filteredPool

def randomAction(pool):
    'Execute a random enabled action from the SUT, catch bugs or add to pool'
    global nbug
    act = sut.randomEnabled(rgen)
    ok = sut.safely(act)
    if not ok:
        nbug += 1
        if (opts.fault):
            captureFault()
        else:
            print "FAILURE LOCATED"
        collectCoverage() # collecting coverage because sut.restart() resets internal coverage
        sut.restart()   
    else:
        if (opts.running):
            runtimeCoverage()
        pool.addTest(sut.test(),sut.state(),set(sut.currStatements()))
    return ok

def collectCoverage():
    'Update the global coverage count for executions on each statement'
    global coverageCount
    for s in sut.currStatements():
        if s not in coverageCount:
            coverageCount[s] = 0
        coverageCount[s] += 1   

def printCoverage():
    'Print the state of the global coverage count for executions on each statement'
    if not coverageCount: # might not be any coverage yet
        return
    sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])
    coverSum = sum(coverageCount.values())
    coverMean = coverSum / (1.0*len(coverageCount))
    print "MEAN COVERAGE IS",coverMean
    for s in sortedCov:
        print s, coverageCount[s]

def calculateThreshold():
    'Determine coverage count for the lowest 10 percent of all statements in global coverage count'
    global coverageCount
    sortedMap = sorted(coverageCount.keys(), key=lambda x: coverageCount[x], reverse=True)
    sortedCov = map(lambda x:(x[1]),sortedMap)
    return percentile(sortedCov, 0.1)

def calculateBelowSet():
    'Calculate the set of statements that are below the threshold'
    global coverageCount, threshold, selectStatements
    selectStatements = set([]) # clear global selectStatements
    sortedMap = sorted(coverageCount.keys(), key=lambda x: coverageCount[x], reverse=False)
    threshold = calculateThreshold() # update global threshold
    for s in sortedMap:
        if coverageCount[s] < threshold:
            selectStatements.add(s) # update global selectStatements
        else:
            break

def calculateMean(statements):
    'Calculate the mean coverage across all statements in the provided set'
    stmtCov = [coverageCount[x] for x in statements]
    return percentile(stmtCov, 0.5)

def captureFault():
    'Print failure state and reduction'
    print "FAILURE LOCATED:"
    print sut.failure()
    print "REDUCING FAILURE:"
    R = sut.reduce(sut.test(),sut.fails, True, True)
    sut.prettyPrintTest(R)
    print sut.failure()
    # output to file for each fault
    fname = 'failure%d.test' % nbugs
    fo = open(fname, "wb")
    fo.write(sut.failure())
    fo.close()


class Pool:
    'Common base class for pools of tests (sequences of actions)'
    poolCount = 0

    def __init__(self, name, pool=None):
        self.name = name           
        self.filter = []
        Pool.poolCount += 1
        if not pool:
            self.pool = []
        else:
            self.pool = pool

    def __len__(self):
        return len(self.pool)

    def setFilter(self, filterSet):
        self.filter = filterSet

    def getFilter(self):
        return self.filter

    def addTest(self, test, state, statements=None):
        if statements:
            self.pool.append((test,state,statements))
        else:
            self.pool.append((test,state,{}))

    def getRandom(self):
        return rgen.choice(self.pool)

    def runFilter(self):
        statPool = []
        for (t,s,c) in self.pool:
            for stmt in c:
                if stmt in self.filter:
                    statPool.append((t,s,c))
                    break
        return statPool

    def displayPoolCount(self):
        print "Number of pools: %d" % Pool.poolCount

    def displayInfo(self):
        print "Name:", self.name, ", Size:", self.sizeOf()

def percentile(N, percent, key=lambda x:x):
    """
    Find the percentile of a list of values.
    source: http://code.activestate.com/recipes/511478/

    @parameter N - is a list of values. Note N MUST BE already sorted.
    @parameter percent - a float value from 0.0 to 1.0.
    @parameter key - optional key function to compute value from each element of N.

    @return - the percentile of the values
    """
    if not N:
        return None
    k = (len(N)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(N[int(k)])
    d0 = key(N[int(f)]) * (c-k)
    d1 = key(N[int(c)]) * (k-f)
    return d0+d1

def update_progress(progress):
    'Display or updates a console progress bar, accepts floats from 0 to 1'
    barLength = 20
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rProgress: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), round(progress*100,2), status)
    sys.stdout.write(text)
    sys.stdout.flush()

def runtimeCoverage():
    'Handler for generating running info on branch and statement coverage'
    elapsed = time.time() - start

    if sut.newBranches() != set([]):
        for b in sut.newBranches():
            print elapsed, len(sut.allBranches()),"New branch", b

    if sut.newStatements() != set([]):
        for s in sut.newStatements():
            print elapsed, len(sut.newStatements()), "New statement", s

def parse_options(argv):
    global opts 
    parser = OptionParser()
    parser.add_option('-t', '--timeout', action="store", type="int", dest="timeout", default=30, 
        help="time in seconds for testing")
    parser.add_option('-s', '--seed', action="store", type="int", dest="seed", default=1, 
        help="seed used for random number generation")
    parser.add_option('-d', '--depth', action="store", type="int", dest="depth", default=100, 
        help="maximum length of a test")
    parser.add_option('-w', '--width', action="store", type="int", dest="width", default=1, 
        help="maximum width of a pool of tests")
    parser.add_option('-f', '--fault', action="store_true", dest="fault", default=False, 
        help="check for faults in the SUT")
    parser.add_option('-c', '--coverage', action="store_true", dest="coverage", default=False, 
        help="produce a final coverage report")
    parser.add_option('-r', '--running', action="store_true", dest="running", default=False, 
        help="produce running info on branch coverage")
    parser.add_option('-p', '--progress', action="store_true", dest="progress", default=False,
        help="provide a progress bar on the console while running")
    parser.add_option('--nuke', action="store_true", dest="nuke")
    (opts, args) = parser.parse_args()

    print "OPTIONS:",opts
    print "ARGS:",args

    if len(args) > 0:
        for idx,arg in enumerate(args):
            if idx == 0:
                opts.timeout = int(arg)
            elif idx == 1:
                opts.seed = int(arg)
            elif idx == 2:
                opts.depth = int(arg)
            elif idx == 3:
                opts.width = int(arg)
            elif idx == 4:
                opts.fault = bool(int(arg))
            elif idx == 5:
                opts.coverage = bool(int(arg))
            elif idx == 6:
                opts.running = bool(int(arg))
            elif idx == 7:
                opts.progress = bool(int(arg))
            else:
                print "Error! Options out of bounds: too many parameters"
                sys.exit(1)

    if opts.timeout <= 0:
        print "Error! Option out of bounds: timeout (-t) option must be greater than 0 seconds."
        sys.exit(1)

    print "------------------------"
    print "OPTIONS:",opts
    print "ARGS:",args

    if opts.nuke:
        sys.exit(1)

if __name__ == "__main__":
    main(sys.argv[1:])