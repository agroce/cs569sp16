import sut
import random
import sys
import time
import math
from optparse import OptionParser
from itertools import compress

def main():
    global sut, coverageCount, nbugs, ntest, start
    sut = sut.sut()
    rgen = random.Random(opts.seed)
    coverageCount = {}
    DEPTH = opts.depth
    ntest = 0
    nbugs = 0

    start = time.time()
    pool = Pool(opts.seed)

    elapsed = time.time()-start
    while elapsed < (0.95 * opts.timeout):
        sut.restart()
        ntest += 1
        if opts.progress and ntest % 300:
            update_progress(elapsed/opts.timeout)
        for s in xrange(0,DEPTH):
            act = sut.randomEnabled(rgen)
            if not executeAction(act):
                break
        updateCov()
        pool.add(sut.test(), sut.state(), sut.currStatements())
        elapsed = time.time()-start
    if opts.progress:
        update_progress(1.0)

    if (opts.coverage):
        sut.internalReport()

def updateCov():
    global coverageCount
    
    for s in sut.currStatements():
        if s not in coverageCount:
            coverageCount[s] = 0
        coverageCount[s] += 1

def captureFault():
    'Print failure state and reduction, save to file'
    print "FAILURE LOCATED:"
    print sut.failure()
    print "REDUCING FAILURE:"
    R = sut.reduce(sut.test(),sut.fails, True, True)
    sut.prettyPrintTest(R)
    print sut.failure()
    # output to file for each fault
    filename = 'failure%d.test' % nbugs
    sut.saveTest(R, filename)

def executeAction(act):
    'Execute action, collect coverage and faults'
    global nbug
    ok = sut.safely(act)
    if not ok:
        nbug += 1
        if (opts.fault):
            captureFault()
        else:
            print "FAILURE LOCATED"
        updateCov() # collecting coverage because sut.restart() resets internal coverage
        sut.restart()   
    if ok and opts.running:
            runtimeCoverage()
    return ok

class Pool:
    'Common base class for pools of tests (sequences of enabled actions)'

    def __init__(self, seed, pool=None):
        self.rgen = random.Random(seed)
        self.nbug = 0
        if not pool:
            self.pool = []
        else:
            self.pool = pool

    def __len__(self):
        return len(self.pool)

    def __percentile(self, N, percent, key=lambda x:x):
        'Find the percentile of a list of values. Source: http://code.activestate.com/recipes/511478/'
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

    def __contains(self, statement):
        for s in [c for (t,s,c) in self.pool]:
            if statement in s:
                return True
        return False

    def add(self, test, state, statements):
        self.pool.append( (test,state,statements) )

    def get(self):
        return self.rgen.choice(self.pool)

    def get(self, index):
        if index < len(self.pool):
            return self.pool[index]
        raise IndexError('Pool index out of bounds')

    def mutate(self):
        rindex = self.rgen.randint(0,len(self.pool))
        (t,s,c) = self.pool[rindex]
        tcopy = list(t)
        i = self.rgen.randint(0,len(tcopy))
        sut.replay(tcopy[:i])
        act = sut.randomEnabled(self.rgen)
        executeAction(act)
        trest = [act]
        for s in tcopy[i+1:]:
            if s[1]():
                trest.append(s)
                executeAction(s)
        tcopy = t[:i] + trest
        self.add(sut.test(),sut.state,set(sut.currStatements()))

    def filter(self, percent):
        filterCov = {k: v for k, v in coverageCount.items() if self.__contains(k)}
        sortedMap = sorted(filterCov.iteritems(), key=lambda (k,v): (v,k), reverse=False)
        sortedCov = map(lambda x:(x[1]), sortedMap)
        threshold = self.__percentile(sortedCov, float(percent))
        bottom = [k for k,v in sortedMap if v < threshold]

        for t,s,c in self.pool:
            x = frozenset(bottom).intersection(c)

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
    (opts, args) = parser.parse_args()

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

if __name__ == "__main__":
    parse_options(sys.argv[1:])
    main()