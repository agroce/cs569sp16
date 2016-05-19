import sut
import random
import sys
import time


depth = 100
BUDGET = int(sys.argv[1])
SEED = int(sys.argv[2])
depth = int(sys.argv[3])
width = int(sys.argv[4])
fault = int(sys.argv[5])
coverage = int(sys.argv[6])
running = int(sys.argv[7])

test = None
count = 0
sut = sut.sut()

random = random.Random()

coverageCount = {}
coverage2 = []
coverage3 = None
coverage4 = 10
defCover = 100
weight = 0
bug = 0

start = time.time()

#def parse_args():
#    parser = argparse.ArgumentParser()
#    parser.add_argument('timeout', type = int, default = 300, help = 'Timeout in seconds (300 default).')
#    parser.add_argument('seed', type = int, default = None, help = 'Random seed (default = None).')
#    parser.add_argument('depth', type = int, default = 10, help = 'Maximum search depth (10 default).')
#    parser.add_argument('width', type = int, default = 10, help = 'Maximum search width (10 default).')
#    parsed_args = parser.parse_args(sys.argv[1:])
#    return (parsed_args, parser)
#
#def make_config(parsed_args, parser):
#    pdict = parsed_args.__dict__
#    key_list = pdict.keys()
#    arg_list = [pdict[k] for k in key_list]
#    Config = namedtuple('Config', key_list)
#    nt_config = Config(*arg_list)
#    return nt_config

'''
def function():
    global fault,correct,bug,sut,R,flag
    flag = 0
    if(fault):
        if not correct:
            bug += 1
            print "Found a failure!"
            print sut.failure()
            print "Reducing.."
            R = sut.reduce(sut.test(),sut.fails, True, True)
            sut.prettyPrintTest(R)
            print sut.failure()
            flag = 1
'''

def main():
    global BUDGET,start,test,sut,storedTest,act,correct,running,coverage3,count,flag,savedTestState,coverageCount,sortedCov,weight,weightedCov,coverage2,bug
    while time.time()-start < BUDGET:
        sut.restart()
        if (random.random() > 0.3) and (test != None):
            #print "Exploiting.."
            sut.backtrack(test)
        storedTest = False
        #print "Testing.."
        for i in xrange(0,depth):
            act = sut.randomEnabled(random)
            correct = sut.safely(act)
            if running:
                if sut.newBranches() != set([]):
                    for d in sut.newBranches():
                        print time.time() - start, len(sut.allBranches()),"New branch",d
            if len(sut.newStatements()) > 0:
                test = sut.state()
                storedTest = True
                if(running):
                    print "Found a statement",sut.newStatements()
            if (not storedTest) and (coverage3 != None) and (coverage3 in sut.currStatements()):
                test = sut.state()
                storedTest = True
            count += 1
            
            
            if not correct:
                if not correct:
                    bug += 1
                    print "Found a failure!"
                    print sut.failure()
                    print "Reducing.."
                    R = sut.reduce(sut.test(),sut.fails, True, True)
                    sut.prettyPrintTest(R)
                    print sut.failure()
#flag = 1

            
#if flag == 1:
                    break
        savedTestState = sut.state()
        for i in sut.currStatements():
            if i not in coverageCount:
                coverageCount[i] = 0
            coverageCount[i] += 1
        sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])

        for i in sortedCov:
            weight = i * (defCover - coverageCount[i])
            if weight > coverage4:
                coverage2.append(weight)
                print "Coverage:", i
#sut.backtrack(sut.state())

    if coverage:
        sut.internalReport()
        sortedCov = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])
        for i in sortedCov:
            print i, coverageCount[i]

    print bug,"failed"
    print "Total actions:",count
    print "Total running time:",time.time()-start
if __name__ == '__main__':
    main()