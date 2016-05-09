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


#class config:
#
#    def __init__(self):
#        self.timeout = int(sys.argv[1])
#        self.seed = int(sys.argv[2])
#        self.depth = int(sys.argv[3])
#        self.width = int(sys.argv[4])
#        self.faults = int(sys.argv[5])
#        self.coverage = int(sys.argv[6])
#        self.running = int(sys.argv[7])



def main():

    '''
    Phase one: BFS
    '''
    parsed_args, parser = parse_args()
    Config = make_config(parsed_args, parser)

    print ('testing using config={}'.format(Config))

    sut.silenceCoverage()
    sut.restart()

    R = random.Random(Config.seed)

    state_queue = [sut.state()]
    visited = []

    max_depth_time = 30

    d = 1
    ntests = 0
    nbugs = 0
    faults_file = "failure"
    coverage_count = []
    start = time.time()
    elapsed = time.time() - start

    while d <= Config.depth:
        print "Depth", d, "Queue size", len(state_queue), "Visited set", len(visited)
        w = 1
        len_queue = len(state_queue)
        ntests += 1

        frontier = []
        depth_start = time.time()
        random.shuffle(state_queue)
        for s in state_queue:
            sut.backtrack(s)
            for a in sut.enabled():

                depth_time = time.time() - depth_start

                if depth_time >= max_depth_time:
                    break

                isGood = sut.safely(a)
                elapsed = time.time() - start

                if Config.running:
                    if sut.newBranches() != set([]):
                        print "Action:", a[0]
                        for b in sut.newBranches():
                           print elapsed, len(sut.allBranches()), "New branch", b
                    if sut.newStatements() != set([]):
                        print "Action:", a[0]
                        for s in sut.newStatements():
                            print elapsed, len(sut.allStatements()), "New statement", s

                if not isGood:
                    nbugs += 1
                    print "Found A Bug! number of bugs:", nbugs
                    print sut.failure()
                    print "Reducing......"

                    reduction = sut.reduce(sut.test(), sut.fails, True, True)

                    sut.prettyPrintTest(reduction)
                    print sut.failure()

                    if Config.faults == 1:
                        f = open(faults_file + str(nbugs) + ".test", "w")
                        print >> f, sut.failure()


                if elapsed >= Config.timeout:
                    break

                s_next = sut.state()

                if s_next not in visited:
                    visited.append(s_next)
                    frontier.append(s_next)

            if depth_time >= max_depth_time:
                break

            if elapsed >= Config.timeout:
                break

            if w <= Config.width:
                w += 1
            else:
                break
            state_queue = frontier

        if elapsed >= Config.timeout:
            print "Stopping Test Due To Timeout, Terminated at Length", len(sut.test())
            print time.time()-start, "TOTAL RUNTIME"
            print ntests, "EXECUTED"
            break
        d += 1

    if Config.coverage == 1:
        sut.internalReport()

    '''
    Phase two: Focusing on the least 1/3 coverage (TODO)
    '''

if __name__ == '__main__':
    main()
