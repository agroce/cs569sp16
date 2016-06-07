import os
import sys

# Appending current working directory to sys.path
# So that user running randomtester from the directory where sut.py is located
current_working_dir = os.getcwd()
sys.path.append(current_working_dir)

import sut as SUT
import random
import time
import sys
import traceback
import argparse
from collections import namedtuple

startprog = time.time()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--timeout', type=int, default=10,
                        help='Timeout in seconds (3600 default).')
    parser.add_argument('-d', '--depth', type=int, default=100,
                        help='Maximum search depth (100 default).')
    parser.add_argument('-w', '--width', type=int, default=1,
                        help='Maximum search width (1 default).')
    parser.add_argument('-s', '--seed', type=int, default=1,
                        help='Random seed (default = 1).')
    parser.add_argument('-o', '--output', type=str, default="failure",
                        help="Filename to save failing test(s).")
    parser.add_argument('-c', '--coverage', action='store_false', default = True,
                        help="Produce internal coverage report at the end.")    
    parser.add_argument('-f', '--fault', action='store_true', default = False,
                        help="Produce failure file." )  
    parser.add_argument('-r', '--running', action='store_false', default = True,
                        help="Produce running branch coverage report.")
    parser.add_argument('-n', '--naction', type=int, default=1,
                        help='Number of initial actions (3 default).')
    parser.add_argument('-m', '--maxaction', type=int, default=20,
                        help='Number of Maximum actions (20 default).')
    parser.add_argument('-a', '--actiontime', type=float, default=0.7,
                        help='Tolerance time of action (0.7 default).')

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
    print('Testing using config={}'.format(config))


    #rand = random.Random(seed)
    rand = random.Random()
    rand.seed(config.seed)
    start = time.time()
    runningtime = time.time()-startprog
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
    bugs = 0
    checkResult = True
    naction = config.naction    # Optimum initial set size 
    maxaction = config.maxaction # Maximum set size
    actiontime = config.actiontime # Action time tolerance 1 second
    elasped = 0.0
    
    while time.time()-startprog < config.timeout:
        sut.restart()
        elapsed = time.time()-startprog
        for d in xrange(0,config.depth):
            depthelasped = time.time()-startprog
            nowelapsed = elasped+depthelasped
            if nowelapsed > config.timeout:
                print "STOPPING TEST DUE TO config.TIMEOUT, TERMINATED AT DEPTH "+str(d)
                print "ACTION SIZE: "+str(naction)
                break
            startaction = time.time() 
            
            for w in xrange(0,config.width):
                widthelasped = time.time()-startprog
                nowelapsed = nowelapsed+widthelasped
                #a = sut.randomEnabled(R)  s
                a = sut.randomEnableds(rand, naction)
                if nowelapsed >= config.timeout:
                        break
                for i in xrange(0,naction):
                    forelapsed = time.time()-startprog
                    nowelapsed = nowelapsed+forelapsed
                    if nowelapsed >= config.timeout:
                        break
                    if a[0] == None:
                        print "TERMINATING TEST DUE TO NO ENABLED ACTIONS"
                        break         

                    nops += 1
                  
                    startOp = time.time()
                    stepOk = sut.safely(a[0])
                    propok = sut.check()


                    if sut.warning() != None:
                        print "SUT WARNING:",sut.warning()
                    opTime += (time.time()-startOp)
                    if (not propok) or (not stepOk):
                        bugs += 1
                        print "TEST FAILED"
                        print "REDUCING..."
                        R = sut.reduce(sut.test(),sut.fails, True, True)
                        sut.prettyPrintTest(R)
                        print sut.failure()
                        if config.fault:
                            filename= config.output +str(bugs)+'.test'
                            sut.saveTest(sut.test(),filename)
                
                    runningelapsed = time.time() - startprog
                    if config.running:
                        if sut.newBranches() != set([]):
                            print "ACTION:",a[i]
                            for b in sut.newBranches():
                                print runningelapsed,len(sut.allBranches()),"New branch",b
                            sawNew = True
                        else:
                            sawNew = False
                        if sut.newStatements() != set([]):
                            print "ACTION:",a[i]
                            print "FOUND NEW STATEMENTS",sut.newStatements()
                            for s in sut.newStatements():
                                print runningelapsed ,len(sut.allStatements()),"New statement",s
                            sawNew = True
                        else:
                            sawNew = False                

                    if runningelapsed  > config.timeout:
                        print "STOPPING TEST DUE TO config.TIMEOUT, TERMINATED AT LENGTH",len(sut.test())
                        break
                    actionelapsed = time.time() - startaction   

                if(actionelapsed > actiontime):
                   if(naction < maxaction):
                        naction+=1    

    if config.coverage:
        sut.internalReport()

    
    print time.time()-startprog, "TOTAL RUNTIME"
    print nops, "TOTAL TEST OPERATIONS"
    print opTime, "TIME SPENT EXECUTING TEST OPERATIONS"
    print bugs,"FAILED"
    
if __name__ == '__main__':
    main()