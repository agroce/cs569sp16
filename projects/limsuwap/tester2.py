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


timeout  = int(sys.argv[1]) # 30 
seed     = int(sys.argv[2]) # 1
depth    = int(sys.argv[3]) # 100
width    = int(sys.argv[4]) # 1
fault    = int(sys.argv[5]) # 0
coverage = int(sys.argv[6]) # 1
running  = int(sys.argv[7]) # 1

startprog = time.time()

def main():
    global failCount,sut,config,reduceTime,quickCount,repeatCount,failures,cloudFailures,R,opTime,checkTime,guardTime,restartTime,nops,ntests
    
    rand = random.Random(seed)

    start = time.time()
    #elapsed = time.time()-start
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
    naction = 3 #optimum initial set size 
    maxaction = 50 #maximum set size
    actiontime = 1 # Action time tolerance 1 second

    
    while runningtime < timeout:
        sut.restart()
        elapsed = time.time()-startprog
        for d in xrange(0,depth):
            elapsed = time.time()-startprog
            if elapsed > timeout:
                break
            startaction = time.time()    
            for w in xrange(0,width):
                elapsed = time.time()-startprog
                #a = sut.randomEnabled(R)  
                a = sut.randomEnableds(rand, naction)
                actionelapsed = time.time() - startaction
                for i in xrange(0,naction):
                    if a[0] == None:
                        print "WARNING: DEADLOCK (NO ENABLED ACTIONS)"
                        
                    if elapsed > timeout:
                        print "STOPPING TEST DUE TO TIMEOUT, TERMINATED AT LENGTH",len(sut.test())
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
                        R = sut.reduce(sut.test(), lambda x: sut.fails(x) or sut.failsCheck(x))
                        sut.prettyPrintTest(R)
                        print sut.failure()
                        if fault:
                            filename='failure'+str(bugs)+'.test'
                            sut.saveTest(sut.test(),filename)
                            for i in range(len(R)):
                                with open(filename,'w') as f:
                                    f.write('\n'+'Bug no.'+str(bugs)+'\n')                          
                                    f.write(str(sut.failure())+'\n')
                                    f.write(str(R)+'\n')    
                        #print "NORMALIZING..."
                        #N = sut.normalize(R, lambda x: sut.fails(x) or sut.failsCheck(x))
                        #sut.prettyPrintTest(N)
                        #print "GENERALIZING..."
                        #sut.generalize(N, lambda x: sut.fails(x) or sut.failsCheck(x))
                        #break
                
                    elapsed = time.time() - startprog
                    if running:
                        if sut.newBranches() != set([]):
                            print "ACTION:",a[i]
                            for b in sut.newBranches():
                                print elapsed,len(sut.allBranches()),"New branch",b
                            sawNew = True
                        else:
                            sawNew = False
                        if sut.newStatements() != set([]):
                            print "ACTION:",a[i]
                            for s in sut.newStatements():
                                print elapsed,len(sut.allStatements()),"New statement",s
                            sawNew = True
                        else:
                            sawNew = False                

                    if elapsed > timeout:
                        print "STOPPING TEST DUE TO TIMEOUT, TERMINATED AT LENGTH",len(sut.test())
                        break 
                if(actionelapsed > actiontime):
                   if(naction < maxaction):
                        naction+=1    

        if elapsed > timeout:
            print "STOPPING TEST DUE TO TIMEOUT, TERMINATED AT LENGTH",len(sut.test())
            break 

    if coverage:
        sut.internalReport()

    print time.time()-startprog, "TOTAL RUNTIME"
    print nops, "TOTAL TEST OPERATIONS"
    print opTime, "TIME SPENT EXECUTING TEST OPERATIONS"
    print bugs,"FAILED"
    
if __name__ == '__main__':
    main()