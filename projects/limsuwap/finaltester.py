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
rand = random.Random()
rand.seed(seed)

def main():
    global failCount,sut,config,reduceTime,quickCount,repeatCount,failures,cloudFailures,R,opTime,checkTime,guardTime,restartTime,nops,ntests
    
    #rand = random.Random(seed)

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
    naction = 3    # Optimum initial set size 
    maxaction = 50 # Maximum set size
    actiontime = 0.4 # Action time tolerance 1 second
    elasped = 0.0
    
    while time.time()-startprog < timeout:
        sut.restart()
        elapsed = time.time()-startprog
        for d in xrange(0,depth):
            depthelasped = time.time()-startprog
            nowelapsed = elasped+depthelasped
            if nowelapsed > timeout:
                print "STOPPING TEST DUE TO TIMEOUT, TERMINATED AT DEPTH "+str(d)
                print "ACTION SIZE: "+str(naction)
                break
            startaction = time.time() 
            
            for w in xrange(0,width):
                widthelasped = time.time()-startprog
                nowelapsed = nowelapsed+widthelasped
                #a = sut.randomEnabled(R)  s
                a = sut.randomEnableds(rand, naction)
                if nowelapsed >= timeout:
                        break
                for i in xrange(0,naction):
                    forelapsed = time.time()-startprog
                    nowelapsed = nowelapsed+forelapsed
                    if nowelapsed >= timeout:
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
                        #sut.prettyPrintTest(R)
                        print sut.failure()
                        if fault:
                            filename='failure'+str(bugs)+'.test'
                            sut.saveTest(sut.test(),filename)
                
                    runningelapsed = time.time() - startprog
                    if running:
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

                    if runningelapsed  > timeout:
                        print "STOPPING TEST DUE TO TIMEOUT, TERMINATED AT LENGTH",len(sut.test())
                        break
                    actionelapsed = time.time() - startaction   

                if(actionelapsed > actiontime):
                   if(naction < maxaction):
                        naction+=1    

    if coverage:
        sut.internalReport()

    
    print time.time()-startprog, "TOTAL RUNTIME"
    print nops, "TOTAL TEST OPERATIONS"
    print opTime, "TIME SPENT EXECUTING TEST OPERATIONS"
    print bugs,"FAILED"
    
if __name__ == '__main__':
    main()