#******** This code is based on the code writing by Pro. Alex in the class and randomtester.py *********
import os
import sut
import random
import sys
import time
import traceback
import argparse
from collections import namedtuple

#This code is taken from randomteser.py
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--timeout', type = int, default = 60, help = 'Timeout in seconds.')
    parser.add_argument('-s', '--seed', type = int, default = 0, help = 'Random seed.')
    parser.add_argument('-d', '--depth', type = int, default = 100, help = 'Search depth.')                                                
    parser.add_argument('-w', '--width', type = int, default = 10, help = 'Width.')
    parser.add_argument('-f', '--faults',  action = 'store_true', help = 'To chech for action faults')
    parser.add_argument('-c', '--coverage', action = 'store_true', help = 'To show coverage report')
    parser.add_argument('-r', '--running', action = 'store_true', help = 'To show running branch coverage report')
    parser.add_argument('-p', '--checkProp', action = 'store_true', help = 'To check for property faults')                    
    parsed_args = parser.parse_args(sys.argv[1:])
    return (parsed_args, parser)

def make_config(pargs, parser):
    pdict = pargs.__dict__
    key_list = pdict.keys()
    arg_list = [pdict[k] for k in key_list]
    Config = namedtuple('Config', key_list)
    nt_config = Config(*arg_list)
    return nt_config      

actCount = 0
bugs = 0
no_tests = 0
i = 0

covCount = {}
leastCov = None
savedTest = None

sut = sut.sut()

parsed_args, parser = parse_args()
config = make_config(parsed_args, parser)

rgen = random.Random(config.seed)

start = time.time()
while time.time()-start < config.timeout:
    for ts in xrange(0,config.width):
        sut.restart()
        no_tests += 1
        if (savedTest != None) and (rgen.random() > 0.8):
           sut.backtrack(savedTest)
        
   
        test = False    
        for s in xrange(0,config.depth):
            act = sut.randomEnabled(rgen)
            ok = sut.safely(act)
            propok = sut.check()   
            if len(sut.newBranches()) > 0:
                savedTest = sut.state()
                test = True
                
            if (not test) and (leastCov != None) and (leastCov in sut.currBranches()):
                savedTest = sut.state()
                test = True
            actCount += 1
            
            #if running=1, print elapsed time, total brach count, new branch if running=0 don't print
            if config.running:
                if sut.newBranches() != set([]):
                    print "ACTION:",act[0]
                    for b in sut.newBranches():
                        print time.time() - start,len(sut.allBranches()),"new branch",b
            
            #if faults=1, check for bugs and store them in files, if faults=0 don't check for bugs.
            if (not ok) and (config.faults):
                print "FAILURE FOUND.....FAILURES ARE STORING IN FILES"
                i += 1
                bugs += 1
                saveFault = 'failure' + str(bugs) + '.test' 
                sut.saveTest(sut.test(), saveFault)
                print "Number bugs found is" ,i
                sut.restart() 
             
                 
            if (not propok) and (config.checkProp):
                print "FAILURE FOUND.....FAILURES ARE STORING IN FILES"
                i += 1
                bugs += 1
                saveFault = 'failure' + str(bugs) + '.test' 
                sut.saveTest(sut.test(), saveFault)
                print "Number bugs found is" ,i
                sut.restart()       
                 
        #To see what is the least covered branch to do experiments on them  
        for s in sut.currBranches():
            if s not in covCount:
                covCount[s] = 0
            covCount[s] += 1    
            sortedCov = sorted(covCount.keys(), key=lambda x: covCount[x])
            leastCov = sortedCov[0]
        
        if (time.time() - start > config.timeout):
            break    

#Take the name of all actions and sort them by their action count
sortedCov = sorted(covCount.keys(), key=lambda x: covCount[x])
 

# if coverage = 1, print internal report            
if config.coverage:
    sut.internalReport()
    
print "TOTAL NUMBER OF BUGS",bugs
print "TOTAL NUMBER OF TESTS",no_tests
print "TOTAL NUMBER OF ACTIONS",actCount
print "TOTAL NUMBER OF RUNTIME",time.time()-start
