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
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('timeout', type=int)
    parser.add_argument('seed', type=int)
    parser.add_argument('depth', type=int)
    parser.add_argument('width', type=int)
    parser.add_argument('faults', type=int,choices=[0,1])
    parser.add_argument('coverage', type=int,choices=[0,1]) 
    parser.add_argument('running', type=int,choices=[0,1]) 
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
    global failCount,t,config,quickCount,repeatCount,failures,cloudFailures,R,opTime,checkTime,guardTime,restartTime,nops,lastact,parts , pt , ptlast
    parsed_args, parser = parse_args()
    config = make_config(parsed_args, parser)
    R = random.Random(config.seed)

    start = time.time()
    elapsed = time.time()-start

    failCount = 0
    quickCount = 0
    repeatCount = 0
    failures = []
    cloudFailures = [] 

    t = SUT.sut()
    
    tacts = t.actions()
    a = None
    sawNew = False

    nops = 0
    opTime = 0.0
    checkTime = 0.0
    guardTime = 0.0
    restartTime = 0.0
    
    lastact = 0
    parts = R.randint(2,10)
    pt = 0
    ptlast = 0
    startRestart = time.time()
    t.restart()        
    restartTime += time.time() - startRestart
    test = []
    
    for s in xrange(0,config.depth):
         acts = tacts
         while True:
                elapsed = time.time() - start
                partsize =  len(acts)/parts
                pt =  R.randint(0,parts-1)
                while pt == ptlast:
                    pt =  R.randint(0,parts-1)
                p = R.randint(pt*partsize,(pt+1)*partsize-1)
                a = acts[p]
                lastact = p
                ptlast = pt
                if a[1]():
                    break
                else:
                    a = None
                acts = acts[:p] + acts[p+1:]
         test.append(a)
         nops += 1
         stepOk = t.safely(a) 
         if not stepOk:
                print "STOPPING TESTING DUE TO FAILED TEST"
                break      
         elapsed = time.time() - start 
         if elapsed > config.timeout:
                print "STOPPING TEST DUE TO TIMEOUT, TERMINATED AT LENGTH",len(test)
                break
         
         stepOk = t.safely(a)
         checkResult = t.check()
         if not checkResult:
                print "STOPPING TESTING DUE TO FAILED TEST"
                break
         if config.running:
            if t.newBranches() != set([]):
                  print "ACTION:",a[0]
                  for b in t.newBranches():
                      print elapsed,len(t.allBranches()),"New branch",b
                  sawNew = True
            else:
                  sawNew = False
            if t.newStatements() != set([]):
                  print "ACTION:",a[0]
                  for s in t.newStatements():
                      print elapsed,len(t.allStatements()),"New statement",s
                  sawNew = True
            else:
                  sawNew = False                

         if elapsed > config.timeout:
            print "STOPPING TEST DUE TO TIMEOUT, TERMINATED AT LENGTH",len(test)
            break                
    print time.time()-start, "TOTAL RUNTIME"
    print nops, "TOTAL TEST OPERATIONS"  
    if config.coverage:
        t.restart()
        print t.report("coverage.out"),"PERCENT COVERED"
        t.internalReport()        
if __name__ == '__main__':
    main()