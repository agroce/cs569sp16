#project milestone1
import sys
import sut
import random
import time
import argparse
import os
import string

from collections import namedtuple

global depth, sut, gene, failCount, actionsCount

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


def make_config(pargs, parser):
    pdict = pargs.__dict__
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

def func1():
    global sut,testSaving,testStored,srun,failCount,R,flag,actionsCount
    flag = 0
    if len(sut.newStatements()) > 0:
        testSaving = sut.state()
        testStored = True
        print "Find statements:",sut.newStatements()
    if (covrageLeast != None):
        if (covrageLeast in sut.currStatements()) and (testStored == 0):
            testSaving = sut.state()
            testStored = True
    actionsCount = actionsCount + 1
    if (srun == 0):
        failCount = failCount + 1
        print "This is failure"
        print sut.failure()
        print "Now reducing.."
        R = sut.reduce(sut.test(),sut.fails, True, True)
        sut.prettyPrintTest(R)            
        print sut.failure()
        flag = 1
def main():
    global start,TIMEBUDGET,sut,testSaving,gene,testStored,act,srun,flag,coverageCount,covrSort,calculateWei,allCoverage,cW,coverageWM,failCount,actionsCount,sd
    while time.time()-start < TIMEBUDGET:
        sut.restart()
        if (testSaving != None) and (gene.random() > 0.3):
            sut.backtrack(testSaving)
        testStored = False
        print "Firstly test the AVL tree"
        for s in xrange(0,100):
            act = sut.randomEnabled(gene)
            srun = sut.safely(act)
            func1()
            if flag == 1:
                break
        for s in sut.currStatements():
            if s not in coverageCount:
                coverageCount[s] = 0
            coverageCount[s] = coverageCount[s] + 1
        covrSort = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])
        print "Secondly calculate weight of the coverage"
        for st in covrSort:
            calculateWei = (allCoverage - coverageCount[st])
            cW = st*calculateWei
            if cW > 25:
                coverageWM.append(cW)
                print "Now I have the statement below coverage:", st

    for sd in covrSort:
        print sd,coverageCount[sd]
    sut.internalReport()    
    print failCount,"FAILED"
    print actionsCount,"TOTAL ACTIONS"
    print time.time()-start,"TOTAL RUNTIME"
if __name__ == '__main__':
    main()
