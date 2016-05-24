import sys
import random
import time
import os
import traceback
import argparse
from collections import namedtuple
import sut



sut  = sut.sut()


def parse_args():
    parser = argparse.ArgumentParser()
        
    parser.add_argument('timeout', type=int, default=60)
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

def failures(sut,bugs, Config, faults_file):
    bugs +=1
    print "FOUND A FAILURE"
    print sut.failure()
    print "REDUCING"
    failPool.append(sut.test())
    collectCoverage()
    R = sut.reduce(sut.test(), sut.fails, True, True)
    
    sut.prettyPrintTest(R)
    print sut.failure()
    



def mutate(test, r, bugs):
    tcopy = list(test)
    i = r.randint(0,len(tcopy))
    act = sut.randomEnabled(r)
    isGood = sut.safely(act)
    if not isGood:
        bugs += 1
        failures(sut)
        sut.restart()
    else:
        trest = [act]
        for s in tcopy[i+1:]:
            if s[1]():
                trest.append(s)
                sut.safely(s)
                tcopy = test[:i]+trest
    return tcopy

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
    bugs = 0
    actCount = 0
    faults_file = "failure"
    coverage_count = {}
    leastCovered = None
    statebuff = []
    start = time.time()
    elapsed = time.time() - start
    
    while d <= Config.depth:
        print "Depth", d, "Size", len(state_queue), "Set", len(visited)
        w = 1
        len_queue = len(state_queue)
        ntests += 1
        
        frontier = []
        depth_start = time.time()
        random.shuffle(state_queue)
        savedTest = False
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
                            print elapsed, len(sut.allBranches()), "New branch", b
                    if sut.newStatements() != set([]):
                        print "Action:", a[0]
                        for s in sut.newStatements():
                            print elapsed, len(sut.allStatements()), "New statement", s
                
                    s_next = sut.state()
                    
                    if s_next not in visited:
                        visited.append(s_next)
                        frontier.append(s_next)
                            
                if not isGood:
                    failures(sut, bugs, Config, faults_file)
                    if Config.faults == 1:
                        sut.saveTest(R, faults_file + str(bugs) + ".test")
                        sut.restart()

                if len(sut.newStatements()) > 0:
                    frontier.insert(0, sut.state())
                    savedTest = True
                if (not savedTest) and (leastCovered != None) and (leastCovered in sut.currStatements()):
                    frontier.insert(0, sut.state())
                    savedTest = True
                            
               
                elapsed = time.time() - start
                if elapsed >= Config.timeout:
                    break
                                        
            if depth_time >= tdepth:
                break
            if elapsed >= Config.timeout:
                break
            if w <= Config.width:
                w += 1
            else:
                break
                                                                        
                                                                    
            statebuff.append((list(sut.test()), set(sut.currBranches())));
                                                                            
                                                                            
        state_queue = frontier
                                                                                
        sortPop = sorted(statebuff,key = lambda x: len(x[1]),reverse=True)
        (t,b) = rgen.choice(statebuff)
        m = mutate(t, rgen, bugs)
        statebuff.append((m, sut.currBranches()))
                                                                                                
                                                                                                
        if elapsed >= Config.timeout:
            print "Stopping Test Due To Timeout, Terminated at Length", len(sut.test())
            print ntests, "EXECUTED"
            break
                                                                                                                    
        for s in sut.currStatements():
            if s not in coverage_count:
                coverage_count[s] = 0
            coverage_count[s] += 1
        sortedCov = sorted(coverage_count.keys(), key=lambda x: coverage_count[x])
        if len(sortedCov) != 0:
            leastCovered = sortedCov[0]
                                                                                                                                                
        d += 1
                                                                                                                                                    
    if Config.coverage == 1:
        sut.internalReport()
    print bugs,"FAILED"
    print "TOTAL ACTIONS",actCount
    print "TOTAL RUNTIME",time.time()-start

if __name__ == '__main__':
    main()
