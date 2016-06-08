#!/usr/bin/python
import random
import time
import math
import os
import sys
import sut
import argparse
from collections import namedtuple
#implementing outliers of least coverages
# parsing parameters

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--timeout', type = int, default = 60, help = 'Timeout in seconds.')
    parser.add_argument('-s', '--seed', type = int, default = None, help = 'Random seed.')
    parser.add_argument('-d', '--depth', type = int, default = 100, help = 'For search depth.')                                                
    parser.add_argument('-w', '--width', type = int, default = 100, help = 'For the Width.')
    parser.add_argument('-f', '--fault', action = 'store_true', help = 'To check for fault')
    parser.add_argument('-c', '--coverage', action = 'store_true', help = 'To show coverage report')
    parser.add_argument('-r', '--running', action = 'store_true', help = 'To show running branch coverage report')
    parser.add_argument('-p', '--checkProp', action = 'store_true', help = 'To check for property')                    
    parsed_args = parser.parse_args(sys.argv[1:])
    return (parsed_args, parser)

def make_config(pargs, parser):
    pdict = pargs.__dict__
    key_list = pdict.keys()
    arg_list = [pdict[k] for k in key_list]
    Config = namedtuple('Config', key_list)
    nt_config = Config(*arg_list)
    return nt_config      

parsed_args, parser = parse_args()
config = make_config(parsed_args, parser)
rgen = random.Random(config.seed)

def mutate(test):
    tcopy = list(test)
    i = rgen.randint(0,len(tcopy))
    e = sut.randomEnabled(rgen)
    sut.safely(e)
    trest = [e]
    for s in tcopy[i+1:]:
        if s[1]():
            trest.append(s)
            sut.safely(s)
    tcopy = test[:i]+trest
    if len(sut.newCurrBranches()) != 0:
        print "NEW BRANCHES DUE TO MUTATION:",sut.newCurrBranches()
    return tcopy


sut = sut.sut();

sut.silenceCoverage()

savedTest = None


actCount = 0

bugs = 0

act = sut.randomEnabled(rgen)
tests = []
start = time.time()
population = []

print "STARTING POP BRANCHCOV",len(sut.allBranches())
print "STARTING POP STATEMENTCOV",len(sut.allStatements())
#tryStutter = (act != None) and (act[1]())
storedTest = False;
while(time.time()< start + config.timeout):
        for ts in xrange(0,config.width):
            sut.restart()
            for b in xrange(0,config.depth):
                act = sut.randomEnabled(rgen)
                ok = sut.safely(act)
                new = False
                actCount += 1
                propok = sut.check()
               
                #if running=1, print elapsed time, total brach count, new branch otherwise don't print
                if config.running:
                    if sut.newBranches() != set([]):
                        print "Entered here"
#                        print "ACTION:",a[0],tryStutter
                        for b in sut.newBranches():
                            print time.time()-start,len(sut.allBranches())," branch",b
                        new = True
                    else:
                        new = False  
                if config.fault:
                    if not ok: 
                        bugs += 1
                        fault = sut.failure();
                        fname = 'fault'+str(bugs)+'.test'
                        sut.saveTest(sut.test(), fname)
                        sut.restart()
                else:
                    if len(sut.newBranches()) != 0:
                        test = sut.test()
                        mut = mutate(test) 
                        print "NEW BRANCHES FOUND",sut.newBranches()
                        tests.append((list(sut.test()), set(sut.currBranches()))) 
                        tests = sorted(tests, reverse=True)[:config.width]
                        #mut = mutate(tests)
                        population.append((mut,sut.currBranches()))
                        RandomMemebersSelection = random.sample(tests,int(float((len(tests))*.20)))
                        for x in RandomMemebersSelection:
                            tests.remove(x)



if config.coverage:
    sut.internalReport()
print "Total Number of bugs",bugs
print "Total number of actions",actCount
print "Total Runtime",time.time()-start
print "FINAL POP BRANCHCOV",len(sut.allBranches())
print "FINAL POP STATEMENTCOV",len(sut.allStatements())    
