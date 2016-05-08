import sut
import sys
import random
import time
import math
import os
import traceback
import argparse
from collections import namedtuple


##TIMEOUT = int(sys.argv[1])

##SEED = int(sys.argv[2])

##DEPTH = int(sys.argv[3])

##WIDTH = int(sys.argv[4])

##FAULTS = int(sys.argv[5])

##COVERAGE = int(sys.argv[6])

##RUNNING = int(sys.argv[7])


bugs = 0
def parse_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('timeout', type=int, default=40)
    parser.add_argument('seed', type=int, default=None)
    parser.add_argument('depth', type=int, default=100)
    parser.add_argument('width', type=int, default=10000)
    parser.add_argument('faults', type=int, default=0, choices=[0, 1])
    parser.add_argument('coverage', type=int, default=0, choices=[0, 1])
    parser.add_argument('running', type=int, default=0, choices=[0, 1])
    parsed_args = parser.parse_args(sys.argv[1:])
                                        
    return (parsed_args, parser)


def make_config(pargs, parser):
    
    pdict = pargs.__dict__
    key_list = pdict.keys()
    arg_list = [pdict[k] for k in key_list]
    Config = namedtuple('Config', key_list)
    nt_config = Config(*arg_list)
    return nt_config

def failures():
        bugs += 1
        print "FOUND A FAILURE"
        print sut.failure()
        print "REDUCING"
        failPool.append(sut.test())
        collectCoverage()
        R = sut.reduce(sut.test(),sut.fails, True, True)
        sut.prettyPrintTest(R)
        print sut.failure()
        sut.restart()

sut=sut.sut()


def main():

    parsed_args, parser = parse_args()
    Config = make_config(parsed_args, parser)
    rgen = random.Random(Config.seed)
    
    print ('testing using config={}'.format(Config))
    
    sut.silenceCoverage()
    sut.restart()
    
    
    state_queue = [sut.state()]
    visited = []
    
    tdepth = 30
    
    d = 1
    ntests = 0
    actCount = 0
    coverage_count = []
    start = time.time()
    
    
    while d <= Config.depth:
        print "Depth", d, "Queue size", len(state_queue), "Visited set", len(visited)
        w = 1
        len_queue = len(state_queue)
        ntests += 1
        
        frontier = []
        depth_start = time.time()
        for s in state_queue:
            sut.backtrack(s)
            
            for a in sut.enabled():
                
                depth_time = time.time() - depth_start
                act = sut.randomEnabled(rgen)
                actCount += 1
                
                if depth_time >= tdepth:
                    break
            
                isGood = sut.safely(a)
                
                if Config.running:
                    if sut.newBranches() != set([]):
                        print "Action:", a[0]
                        for b in sut.newBranches():
                            print elapsed, len(sut.allBranches()), "New Branch", b
                    if sut.newStatements() != set([]):
                        print "Action:", a[0]
                        for s in sut.newStatements():
                            print elapsed, len(sut.allStatements()), "New Statement", s
                
                if not isGood:
                    failures()
                    
                    reduction = sut.reduce(sut.test(), sut.fails, True, True)
                    
                    sut.prettyPrintTest(reduction)
                    print sut.failure()
                    
                    if Config.faults == 1:
                        f = open(faults_file, "w")
                        print >> f, sut.failure()
                            
                            
                elapsed = time.time() - start
                        
                if elapsed >= Config.timeout:
                    break
                                    
                s_next = sut.state()
                                        
                if s_next not in visited:
                    visited.append(s_next)
                    frontier.append(s_next)
                                                    
                if depth_time >= tdepth:
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
                    break
                d += 1
                                
    if Config.coverage == 1:
        sut.internalReport()
    print bugs,"FAILED"
    print "TOTAL ACTIONS",actCount
    print "TOTAL RUNTIME",time.time()-start


if __name__ == '__main__':
    main()
