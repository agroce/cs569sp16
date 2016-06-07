import sut
import sys
import random
import time
import math
import os
#implementing outliers of least coverages
# parsing parameters

TIME_BUDGET = int(sys.argv[1])

SEED = int(sys.argv[2])

DEPTH = int(sys.argv[3])

WIDTH = int(sys.argv[4])

FAULT_CHECK = int(sys.argv[5])

COVERAGE_REPORT = int(sys.argv[6])

RUNNING_DETAIL = int(sys.argv[7])


# init objects and parameters
sut=sut.sut()
sut.silenceCoverage()
rand = random.Random()
rand.seed(SEED)

coverageCount = {}

new_state = []
new_statement_by_state = []

selected_state = []
k_selected = []

state_queue = []
state_visited = []

failure_file = "failure"
bug_no = 0;

#define sub-routines
def randomAction():
    global bug_no, time_start, allAction, ii
    action = sut.randomEnabled(rand)
    ok = sut.safely(action)
    elapsed = time.time() - time_start
    if RUNNING_DETAIL:
        if len(sut.newBranches()) > 0:
            print "ACTION:", action[0]
            for b in sut.newBranches():
                print elapsed, len(sut.allBranches()), "New branch", b

    if not ok:  # found a bug
        bug_no += 1
        print "FOUND A BUG! #", bug_no
        print sut.failure()
        # write the bug to file if FAULT_ARGUMENT is enabled
        if (FAULT_CHECK):
            filename = failure_file + str(bug_no) + ".test"
            sut.saveTest(sut.test(), filename )
        print "time: ", time.time() - time_start
    return ok

def runAct(action):
    global bug_no, time_start
    ok = sut.safely(action)
    elapsed = time.time() - time_start
    if RUNNING_DETAIL:
        if len(sut.newBranches()) > 0:
            print "ACTION:", action[0]
            for b in sut.newBranches():
                print elapsed, len(sut.allBranches()), "New branch", b
    if not ok:  # found a bug
        bug_no += 1
        print "FOUND A BUG in runAct! #", bug_no
        print sut.failure()
        # write the bug to file if FAULT_ARGUMENT is enabled
        if (FAULT_CHECK):
            filename = failure_file + str(bug_no) + ".test"
            sut.saveTest(sut.test(), filename)
        print "time: ", time.time() - time_start
    return ok

def mutation(test):
    global time_start
    elapsed = time.time() - time_start
    tcopy = list(test)
    i = rand.randint(0, len(tcopy))
    sut.replay(tcopy[:i])
    e = sut.randomEnabled(rand)
    runAct(e)
    trest = [e]
    for s in tcopy[i + 1:]:
        if s[1]():
            trest.append(s)
            runAct(s)
    tcopy = test[:i] + trest
    if(RUNNING_DETAIL):
        if len(sut.newCurrBranches()) != 0:
            print "ACTION: (a list of act in mutation)"
            for b in sut.newCurrBranches():
                print elapsed, len(sut.allBranches()), "New branch", b
    return tcopy

def crossover(test1, test2):
    global time_start
    elapsed = time.time() - time_start
    tcopy = list(test1)
    i = rand.randint(0, len(tcopy))
    sut.replay(tcopy[:i])
    trest = []
    for s in test2[i:]:
        if s[1]():
            trest.append(s)
            runAct(s)
    tcopy = test1[:i] + trest
    if (RUNNING_DETAIL):
        if len(sut.newCurrBranches()) != 0:
            print "ACTION: (a list of act in crossover)"
            for b in sut.newCurrBranches():
                print elapsed, len(sut.allBranches()), "New branch", b
    return tcopy




# begin testing
time_start = time.time()
curDepth = 1
state_queue = [sut.state()]

# Phase 1 : run random test in TIME_BUDGET/4 seconds with depth = DEPTH to find out k statements that we rarely cover

TIME_PHASE1 = TIME_BUDGET / 2
print "PHASE 1..."
while(time.time()< time_start + TIME_PHASE1):
    sut.restart()
    for d in xrange(0,DEPTH):
        ok = randomAction()
        if not ok:
            break
        if(len(sut.newStatements())>0): # we found some new statements. Of course such statement coverages are least, so save its state for later use
            new_state.append(sut.state())
            new_statement_by_state.append(sut.newStatements())
    for s in sut.currStatements():
        if s not in coverageCount:
            coverageCount[s]=0
        coverageCount[s] +=1

# find mean & std to filter outliers
sortedCoverage = sorted(coverageCount.keys(),key=lambda x:coverageCount[x])

threshold =  coverageCount[sortedCoverage[3]]
print "Threshold: " , threshold
# filter to keep only states of threshold-least coverage
for s in sortedCoverage:
    #print coverageCount[s]
    if coverageCount[s]> threshold:
        break
    for k in k_selected:
        if s in new_statement_by_state[k]:
            continue
    for k in xrange(0,len(new_statement_by_state)):
        if s in new_statement_by_state[k]:
            k_selected.append(k)

for k in k_selected:
    selected_state.append(new_state[k])

print bug_no, " BUGS FOUND in PHASE 1"

if (COVERAGE_REPORT):
    sut.internalReport()

# PHASE 2
#exploit states of k least coverages to explore new statements
print "PHASE 2..."
TIME_PHASE2 = TIME_BUDGET - TIME_PHASE1

all_state =[]
new_statement_by_state = []
i = 0;
time_start2 = time.time()
time_out = 0

while (time.time() < time_start2 + TIME_PHASE2 and time_out==0):
    for i in xrange(0, len(selected_state) - 1):
        cur_state_1 = selected_state[i]
        sut.restart()
        sut.backtrack(cur_state_1)
        if(rand.random()>0.3):
            for d in xrange(0, DEPTH):
                ok = randomAction()
                if (len(sut.newStatements()) > 0):  # we found some new statements. Of course such statement coverages are least, so save it for later use
                    print "Found new statement!"
                    d = 0
                    if ok:
                        cur_state_1 = sut.state()
                        selected_state[i] = sut.state()
                if (time.time() > time_start2 + TIME_PHASE2):
                    time_out = 1
                    break
            if time_out == 1:
                break
        else:
            t1 = sut.test()
            if (rand.random() < 0.75):
                if (time.time() > time_start2 + TIME_PHASE2):
                    time_out = 1
                    break
                mutation(t1)
                selected_state[i] = sut.state()
            else:
                for j in xrange(1, len(selected_state)):
                    if (time.time() > time_start2 + TIME_PHASE2):
                        time_out = 1
                        break
                    if j == i:
                        continue
                    cur_state_2 = selected_state[j]
                    sut.restart()
                    sut.backtrack(cur_state_2)
                    t2 = sut.test()
                    crossover(t1, t2)
                    selected_state[j] = sut.state()
                if time_out==1:
                    break
        if time_out==1:
            break
    if (time_out == 1):
        break

print bug_no, " BUGS FOUND"
print "total running time: ", time.time() - time_start

if (COVERAGE_REPORT):
    sut.internalReport()