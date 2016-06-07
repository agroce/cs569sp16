import os
import sys

current_working_dir = os.getcwd()
sys.path.append(current_working_dir)

from collections import namedtuple
import sut as SUT
import random
import time
import traceback
import argparse

sut  = SUT.sut()


def parse_args():
     parser = argparse.ArgumentParser()

     parser.add_argument('timeout', type=int, default=60, help='Timeout in seconds. (60 default)')
     parser.add_argument('seed', type=int, default=None, help='Random seed. (default = None)')
     parser.add_argument('depth', type=int, default=100, help='Maximum search depth. (100 default)')
     parser.add_argument('width', type=int, default=10000, help='Maximum memory. (10000 default)')
     parser.add_argument('faults', type=int, default=0, choices=[0, 1], help='Check for faults or not. 1 for check, 0 for do not check (0 default)')
     parser.add_argument('coverage', type=int, default=0, choices=[0, 1] ,help='report coverage or not. 1 for report, 0 for do not report(0 default)')
     parser.add_argument('running', type=int, default=0, choices=[0, 1], help='Produce running branch coverage report.')
     parsed_args = parser.parse_args(sys.argv[1:])

     return (parsed_args, parser)


def make_config(pargs, parser):

     pdict = pargs.__dict__
     key_list = pdict.keys()
     arg_list = [pdict[k] for k in key_list]
     Config = namedtuple('Config', key_list)
     nt_config = Config(*arg_list)
     return nt_config


def saveFaults(sut, nbugs, Config, faults_file):

    sut.prettyPrintTest(sut.test())
    print sut.failure()

    if Config.faults == 1:
        sut.saveTest(sut.test(), faults_file + str(nbugs) + ".test")




def main():

    parsed_args, parser = parse_args()
    Config = make_config(parsed_args, parser)

    print ('testing using config={}'.format(Config))

    sut.silenceCoverage()
    sut.restart()

    R = random.Random()
    R.seed(Config.seed)

    start = time.time()
    explore = 0.7
    actCount = 0
    nbugs = 0
    faults = "failure"
    savedTest = None
    coverageCount = {}
    leastCovered = None
    ntests = 0

    while time.time() - start < Config.timeout:
        sut.restart()
        if (savedTest != None) and (R.random() > explore):
            print "EXPLOITING"
            sut.backtrack(savedTest)
        storedTest = False

        for d in xrange(0, Config.depth):
            act = sut.randomEnabled(R)

            ok = sut.safely(act)

            if len(sut.newStatements()) > 0:
                savedTest = sut.state()
                storedTest = True
                print "FOUND NEW STATEMENTS",sut.newStatements()
            if (not storedTest) and (leastCovered != None) and (leastCovered in sut.currStatements()):
                savedTest = sut.state()
                storedTest = True

            elapsed = time.time() - start
            actCount += 1

            if Config.running:
                if sut.newBranches() != set([]):
                    print "ACTION:", act[0]
                    for b in sut.newBranches():
                        print time.time()-start, len(sut.allBranches()), "New branch", b
                if sut.newStatements() != set([]):
                    print "ACTION:", act[0]
                    for s in sut.newStatements():
                        print time.time()-start, len(sut.allStatements()),"New statement",s

            if not ok:
                nbugs += 1
                saveFaults(sut, nbugs, Config, faults)
                sut.restart()



            if elapsed >= Config.timeout:
                print "Stopping Test Due To Timeout, Terminated at Length", len(sut.test())
                print time.time()-start, "TOTAL RUNTIME"
                break


        for s in sut.currStatements():
            if s not in coverageCount:
                coverageCount[s] = 0
            coverageCount[s] += 1
        sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])
        leastCovered = sortedCov[0]
        print "LEAST COVERED STATEMENT IS",leastCovered,coverageCount[leastCovered]

    if Config.coverage == 1:
        sut.internalReport()
    print nbugs,"FAILED"
    print "TOTAL ACTIONS",actCount
    print "TOTAL RUNTIME",time.time()-start
if __name__ == '__main__':
    main()
