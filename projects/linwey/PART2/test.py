import sut
import random
import sys
import time

BUDGET = int(sys.argv[1])
SEED = int(sys.argv[2])
WIDTH = int(sys.argv[3])
FAULTS = int(sys.argv[4])
COVERAGE = int(sys.argv[5])
RUNNING = int(sys.argv[6]) #parameters paring here
## 

rgen = random.Random()
sut = sut.sut()


collected_test = None
action_cnt = 0
bugfound = 0
coverage_cnt = {}
dis_weight_below_bm = []
lst_coverage = None
dis_weight = 0


start = time.time()

def backtrack():
	if (collected_test != None) and (rgen.random() > 1.0):
		sut.backtrack(collected_test)

#def dis_weight_dis(sorted_cov)
#	for i in sorted_coverage:
#        dis_weight = (100 - coverage_cnt[i])
#        dis_weightedCov = i * dis_weight
#        if dis_weightedCov > 15:
#            dis_weight_below_bm.append(dis_weightedCov)
#            print "statement below coverage is showing here:", i
def newState():
    global rgen,sut,collected_test,storedTest,action_cnt,bugfound
    for i in xrange(0,100):
        action = sut.randomEnabled(rgen)
        no_bug_found = sut.safely(action)
        if len(sut.newStatements()) > 0:
            collected_test = sut.state()
            storedTest = True
            print "new statement collected here",sut.newStatements()
        if (not storedTest) and (lst_coverage != None) and (lst_coverage in sut.currStatements()):

            collected_test = sut.state()
            storedTest = True
        action_cnt += 1
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
    print "Step 01: Start Test"
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
            print "statement below coverage is showing here:", i

sut.internalReport()

for i in sorted_coverage:
    print i, coverage_cnt[i]

print bugfound,"FAILED"
print "overall actions",action_cnt
print "overall runtime",time.time()-start