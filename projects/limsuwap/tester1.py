import os
import sys

# Appending current working directory to sys.path
# So that user running randomtester from the directory where sut.py is located
current_working_dir = os.getcwd()
sys.path.append(current_working_dir)

import sut as SUT
import random
import time
import traceback
import argparse
from collections import namedtuple

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--depth', type=int, default=100,
                        help='Maximum search depth (100 default).')
    parser.add_argument('-w', '--width', type=int, default=1,
                        help='Maximum search width (1 default ).')
    parser.add_argument('-t', '--timeout', type=int, default=30,
                        help='Timeout in seconds (3600 default).')
    parser.add_argument('-s', '--seed', type=int, default=None,
                        help='Random seed (default = None).')
    parser.add_argument('-f', '--fault', type=int, default=None,
                        help="Set failed logging")
    parser.add_argument('-c', '--coverage', type=int, default=1,
                        help="Produce internal coverage report at the end, as sanity check on coverage.py results.") 
    parser.add_argument('-r', '--running', type=int, default=0,
                        help="Produce running branch coverage report.")
    parser.add_argument('-o', '--output', type=str, default=None,
                        help="Filename to save failing test(s).")
    parser.add_argument('-u', '--uncaught', action='store_true',
                        help='Allow uncaught exceptions in actions.')
    
    parsed_args = parser.parse_args(sys.argv[1:])
    return (parsed_args, parser)

def make_config(pargs, parser):
    """
    Process the raw arguments, returning a namedtuple object holding the
    entire configuration, if everything parses correctly.
    """
    pdict = pargs.__dict__
    # create a namedtuple object for fast attribute lookup
    key_list = pdict.keys()
    arg_list = [pdict[k] for k in key_list]
    Config = namedtuple('Config', key_list)
    nt_config = Config(*arg_list)
    return nt_config  

def main():
    global failCount,sut,config,reduceTime,quickCount,repeatCount,failures,cloudFailures,R,opTime,checkTime,guardTime,restartTime,nops,ntests
    
    parsed_args, parser = parse_args()
    config = make_config(parsed_args, parser)
    print('Random testing using config={}'.format(config))
    R = random.Random(config.seed)

    start = time.time()
    elapsed = time.time()-start

    sut = SUT.sut()
    tacts = sut.actions()
    a = None
    sawNew = False

    nops = 0
    ntests = 0
    reduceTime = 0.0
    opTime = 0.0
    checkTime = 0.0
    guardTime = 0.0
    restartTime = 0.0

    checkResult = True
    
    for d in xrange(0,config.depth):
        
        for w in xrange(0,config.width):
        
            startGuard = time.time()

            a = sut.randomEnabled(R)   

            if a == None:
                print "WARNING: DEADLOCK (NO ENABLED ACTIONS)"
                

            if elapsed > config.timeout:
                print "STOPPING TEST DUE TO TIMEOUT, TERMINATED AT LENGTH",len(sut.test())
                break
            if a == None:
                print "TERMINATING TEST DUE TO NO ENABLED ACTIONS"
                break         

            nops += 1

                
            startOp = time.time()
            stepOk = sut.safely(a)
            propok = sut.check()
            if sut.warning() != None:
                print "SUT WARNING:",sut.warning()
            opTime += (time.time()-startOp)
            if (not propok) or (not stepOk):
                print "TEST FAILED"
                print "REDUCING..."
                R = sut.reduce(sut.test(), lambda x: sut.fails(x) or sut.failsCheck(x))
                sut.prettyPrintTest(R)
                print "NORMALIZING..."
                N = sut.normalize(R, lambda x: sut.fails(x) or sut.failsCheck(x))
                #sut.prettyPrintTest(N)
                sut.generalize(N, lambda x: sut.fails(x) or sut.failsCheck(x))
                break
                
            elapsed = time.time() - start
            if config.running:
                if sut.newBranches() != set([]):
                    print "ACTION:",a[0]
                    for b in sut.newBranches():
                        print elapsed,len(sut.allBranches()),"New branch",b
                    sawNew = True
                else:
                    sawNew = False
                if sut.newStatements() != set([]):
                    print "ACTION:",a[0]
                    for s in sut.newStatements():
                        print elapsed,len(sut.allStatements()),"New statement",s
                    sawNew = True
                else:
                    sawNew = False                

            if elapsed > config.timeout:
                print "STOPPING TEST DUE TO TIMEOUT, TERMINATED AT LENGTH",len(sut.test())
                break    

    if config.coverage:
        sut.internalReport()
    print time.time()-start, "TOTAL RUNTIME"
    print nops, "TOTAL TEST OPERATIONS"
    print opTime, "TIME SPENT EXECUTING TEST OPERATIONS"
    #print len(sut.allBranches()),"BRANCHES COVERED"
    #print len(sut.allStatements()),"STATEMENTS COVERED"
    
if __name__ == '__main__':
    main()