#cs569
#final tester
#Qi Wang(wangq5)
#932-439-151
import sys
import sut
import random
import time
import argparse
import os
import string

from collections import namedtuple

global running, depth, sut, gene, failCount, actionsCount

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('timeout', type= int, 
        default= 300, help='Timeout in seconds.')
    parser.add_argument('seed', type= int, 
        default= 100, help='Seed for Python random.random object used for random number generation')
    parser.add_argument('depth', type=int, 
        default= 100, help='maximum depth of a test')
    parser.add_argument('width', type=int, 
        default= 10, help='maximum memory/BFS queue/other')
    parser.add_argument('fault', type=int, 
        default= 0, help='Faults display')
    parser.add_argument('coverage', type=int, 
        default= 0, help='Produce coverage report')
    parser.add_argument('running', type=int,  
        default= 0, help='Produce running info on branch coverage')
    parsed_args = parser.parse_args(sys.argv[1:])
    return (parsed_args, parser)


def make_config(parsed_args, parser):
    pdict = parsed_args.__dict__
    key_list = pdict.keys()
    arg_list = [pdict[k] for k in key_list]
    Config = namedtuple('Config', key_list)
    nt_config = Config(*arg_list)
    return nt_config   

gene = random.Random()
sut = sut.sut()

failCount = 0
actionsCount = 0
coverageCount = {}
coverageWM = []
covrageLeast = None
testSaving = None
calculateWei = 0
allCoverage = 100
TIMEBUDGET = int(sys.argv[1])
start = time.time()

elap = 0

def findFail():
    global sut,testSaving,testStored,srun,failCount,R,flag,actionsCount,filename
    flag = 0
    if len(sut.newStatements()) > 0:
        testSaving = sut.state()
        testStored = True
        print "Find New statement:",sut.newStatements()
    if (covrageLeast != None):
        if (covrageLeast in sut.currStatements()) and (testStored == 0):
            testSaving = sut.state()
            testStored = True
    actionsCount = actionsCount + 1
    if (srun == 0):
        failCount = failCount + 1
        print "This is failure",failCount
        print sut.failure()
        print "Now reducing..."
        R = sut.reduce(sut.test(),sut.fails, True, True)
        sut.prettyPrintTest(R)            
        print sut.failure()
        filename ='failure%d.test'%failCount
        sut.saveTest(R,filename)
        flag = 1

def mutat(test):
    global start,tc
    elapsed = time.time() - start
    tc = list(test)
    i = gene.random(0, len(tc))
    sut.replay(tc[:i])
    e = sut.randomEnabled(gene)
    findFail()
    trest = [e]
    for s in tc[i + 1:]:
        if s[1]():
            trest.append(s)
            findFail()
    tc = test[:i] + trest
    if len(sut.newCurrBranches()) != 0:
            print "ACTION:",act[0]
            for b in sut.newCurrBranches():
                print elapsed, len(sut.allBranches()), "New branch", b
    return tc


def crossover(t1, t2):
    global start
    elapsed = time.time() - start
    tc = list(test1)
    i = gene.random(0, len(tc))
    sut.replay(tc[:i])
    trest = []
    for s in test2[i:]:
        if s[1]():
            trest.append(s)
            findFail()
    tc = test1[:i] + trest
    return tc


def main():
    global running,start,TIMEBUDGET,sut,testSaving,gene,testStored,act,srun
    global flag,coverageCount,covrSort,calculateWei,allCoverage,cW
    global coverageWM,failCount,actionsCount,sd
    #global running,possible
    global config
    #s_state=[]
    #i=0;
    #global lastAddCoverage
    belowMeanCoverage = set([])
    fullPoll = []
    parsed_args, parser = parse_args()
    config = make_config(parsed_args, parser)
    
    while time.time()-start < TIMEBUDGET:
        sut.restart()
        if (testSaving != None) and (gene.random() > 0.3):
            sut.backtrack(testSaving)
        testStored = False
        
        print "Firstly test the AVL tree"
        for s in xrange(0,config.depth):
            act = sut.randomEnabled(gene)
            srun = sut.safely(act)
            if config.running:
            	if sut.newBranches() != set([]):
            		for d in sut.newBranches():
            			print time.time()-start,len(sut.allBranches()),"New branch",d
            findFail()
            if flag == 1:
                break
        

        for sa in sut.currStatements():
            if sa not in coverageCount:
                coverageCount[sa] = 0
            coverageCount[sa] = coverageCount[sa] + 1
        covrSort = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])
        
        #coverSum = sum(coverageCount.values())
        #coverMean = coverSum / (1.0*len(coverageCount))
        #print "the mean of coverage is:",coverMean
        #for st in covrSort:
            #print st, coverageCount[st]
         #   if coverageCount[st]<coverMean:
          #      belowMeanCoverage.add(st)
           # else:
            #    break
        #print len(belowMeanCoverage), "statement below the mean coverage out of the total coverage:",len(coverageCount)
        
        for st in covrSort:
            if st*(allCoverage-coverageCount[st])>25:
                coverageWM.append(st*(allCoverage-coverageCount[st]))
                print "statement below coverage:",st

        
    for sd in covrSort:
        print sd,coverageCount[sd]
    
    sut.internalReport()    
    
    print failCount,"FAILED"
    print len(sut.allBranches()),"BRANCH"
    print actionsCount,"TOTAL ACTIONS"
    print time.time()-start,"TOTAL RUNTIME"

if __name__ == '__main__':
    main()
