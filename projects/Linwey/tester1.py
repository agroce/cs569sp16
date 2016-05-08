import sut
import random
import sys
import time

BUDGET = int(sys.argv[1])
SEED = int(sys.argv[2])
DEPTH = int(sys.argv[3])
WIDTH = int(sys.argv[4])
FAULTS = int(sys.argv[5])
COVERAGE = int(sys.argv[6])
RUNNING = int(sys.argv[7]) #parameters paring here


rgen = random.Random()
sut = sut.sut()
start = time.time()

collected_test = None
action_cnt = 0
bugfound = 0
coverage_cnt = {}
dis_weight_below_bm = []
lst_coverage = None
dis_weight = 0



def backtrack():
	if (collected_test != None) and (rgen.random() > 0.5):
		sut.backtrack(collected_test)

def newState():
    global rgen,sut,collected_test,storedTest,action_cnt,bugfound
    for i in xrange(0,DEPTH):
        action = sut.randomEnabled(rgen)
        no_bug_found = sut.safely(action)
        if RUNNING:
            if sut.newBranches() != set([]):
                for d in sut.newBranches():
                    print time.time() - start,len(sut.allBranches()),"New Branches",d
        if len(sut.newStatements()) > 0:
            collected_test = sut.state()
            storedTest = True
            print "new statement:",sut.newStatements()
        if (not storedTest) and (lst_coverage != None) and (lst_coverage in sut.currStatements()):

            collected_test = sut.state()
            storedTest = True
        action_cnt += 1
        if FAULTS:    
            if not no_bug_found:
                bugfound += 1
                print "A failure happened here."
                rds = sut.reduce(sut.test(),sut.fails, True, True)
                sut.prettyPrintTest(rds)
                print sut.failure()
                break

while time.time()-start < BUDGET:
    sut.restart()
    backtrack()
    storedTest = False
    newState()
    for i in sut.currStatements():
        if i not in coverage_cnt:
            coverage_cnt[i] = 0
        coverage_cnt[i] += 1
    sorted_coverage = sorted(coverage_cnt.keys(), key=lambda x: coverage_cnt[x])
    print "Step 02: destribution the dis_weight"


    for i in sorted_coverage:
        dis_weight = (100 - coverage_cnt[i])
        dis_weightedCov = i * dis_weight
        if dis_weightedCov > 15:
            dis_weight_below_bm.append(dis_weightedCov)
            print "statement below coverage:", i




for i in sorted_coverage:
    print i, coverage_cnt[i]

if COVERAGE:
    sut.internalReport()

print bugfound,"FAILED FOUND"
print "overall actions",action_cnt
print "overall runtime",time.time()-start