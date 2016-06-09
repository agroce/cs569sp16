import glob
import subprocess
import scipy
import scipy.stats
import os

testers = [] #["SWARM","PURE"]
testers.extend (glob.glob("*/finaltester.py"))

printGnuplot = False

data1 = []
data2 = []
data3 = []
sbcov = {}

handled = []

n = 0
s = 0
for t in testers:
    s += 1
    student = t.split("/")[0]
    if student == "alizades":
        continue
    if student in handled:
        continue
    handled.append(student)
    res = sorted(glob.glob(student + "*.tout"))
    for f in res:
        f2 = f.replace("SAHARFIX","alizades")
        thestudent = f2.split(".")[0]
        if thestudent not in sbcov:
            sbcov[thestudent] = {}
        n += 1
        scov = 0
        bcov = 0
        timeout = ""
        crashed = ""
        internalb = "NOBRANCHES"
        internals = "NOSTATEMENTS"
        neverPrinted = True
        for l in open(f):
            if ("branch" in l) or ("Branch" in l):
                if "(u" not in l:
                    pass
                else:
                    bcov = l.split()[1]
                    branch = l.split("(u")[1]
                    if branch not in sbcov[thestudent]:
                        sbcov[thestudent][branch] = True
            if "statement" in l:
                scov = l.split()[1]
            if "!TIMEOUT!" in l:
                timeout = "TIMEOUT!"
            if "!CRASHED!" in l:
                timeout = "CRASHED!"                
            if "TSTL BRANCH COUNT" in l:
                internalb = l.split()[-1]
            if "TSTL STATEMENT COUNT" in l:
                internals = l.split()[-1]                
        #print student,f,"RUNNING:",bcov,"BRANCHES:",internalb,"STATEMENTS:",internals,timeout,crashed
        if printGnuplot:
            print n,s,bcov,"# GNUPLOT"
        if (crashed == ""):
            data1.append((f2,bcov))
            if internals != "NOSTATEMENTS":
                data2.append((f2,internals))
            else:
                data2.append((f2,0))
            if internalb != "NOBRANCHES":
                data3.append((f2,internalb))
            else:
                data3.append((f2,bcov))

#print "\n\nSORTED BY BEST BRANCH COVERAGE RUNNING TOTAL"
#data1 = sorted(data1,key=lambda p:p[1],reverse=True)

#for (s,b) in data1:
#    print s,b

#print "\n\nSORTED BY BEST TOTAL STATEMENT COVERAGE"
#data2 = sorted(data2,key=lambda p:int(p[1]),reverse=True)

#for (s,b) in data2:
#    print s,b    
            
#print "\n\nSORTED BY EITHER BRANCH COVERAGE METHOD"
#data3 = sorted(data3,key=lambda p:int(p[1]),reverse=True)

#for (s,b) in data3:
#    print s,b

sdata = {}
for (s,b) in data3:
    student = s.split(".")[0]
    if student not in sdata:
        sdata[student] = []
    sdata[student].append(int(b))
print "MEAN BRANCH COVERGE OVER",len(sdata[student]),"RUNS"

data4 = []
for s in sdata:
    data4.append((s,scipy.mean(sdata[s]),len(sdata[s]),scipy.std(sdata[s])))

rank = 1
ranks = {}
data4 = sorted(data4,key=lambda p:p[1],reverse=True)

for (s,b,l,sdev) in data4:
    ranks[s] = rank
    rank += 1

rank = 1
tbrank = {}

for s in sorted(sbcov.keys(), key=lambda x:len(sbcov[x]),reverse = True):
    tbrank[s] = rank
    rank += 1

bmeans = {}
    
rank = 1    
for (s,b,l,sdev) in data4:
    print "#"+str(rank)+":",s,"BRANCHES MEAN",round(b,2),"SD",round(sdev,2),"/",len(sbcov[s]),"TOTAL BRANCHES (#"+str(tbrank[s])+")",l,"EXPERIMENTS"
    bmeans[s] = b
    rank += 1
    for (s2,b2,l2,sdev2) in data4:
        if (b2 < b):
            p = scipy.stats.ranksums(sdata[s], sdata[s2]).pvalue
            #p = scipy.stats.ttest_ind(sdata[s][:sl], sdata[s2][:sl],equal_var=False).pvalue
            if p <= 0.05:
                print "  RANK-SUM STATISTICALLY SIGNIFICANTLY BETTER THAN",s2,"(#" + str(ranks[s2]) + ")","p-value =",p
                break    


bugs = {}
students = {}
studentruns = {}
allruns = []

for f in glob.glob("sympytests.*/*/*.test"):
    fout = f + ".out"
    if not os.path.exists(fout):
        print "RUNNING",f
        subprocess.call(["python ~/tstl/utilities/replay.py " + f + " >& " + fout],shell=True)

for f in glob.glob("sympytests.*/*/*.test.out"):
    student = f.split("/")[0].split(".")[1]
    if student == "alizades":
        continue
    if student == "SAHARFIX":
        student = "alizades"
    if student not in studentruns:
        studentruns[student] = {}
    for l in open(f):
        if l[0] == "(":
            bug = l[:-1]
    run = f.split("/")[1]
    bug = bug.split("<traceback object")[0]
    bug = bug.split("of complex")[0]
    bug = bug.split("given: (")[0]
    bug = bug.split("NotAlgebraic(")[0]            
    #print student, bug
    if run not in studentruns[student]:
        studentruns[student][run] = []
    if run not in allruns:
        allruns.append(run)
    studentruns[student][run].append(bug)
    if bug not in bugs:
        bugs[bug] = []
    bugs[bug].append(student)
    
    if student not in students:
        students[student] = []
    students[student].append(bug)

bugsort = sorted(bugs.keys(), key = lambda x:len(set(bugs[x])))

bugids = {}

bugid = 1

print "*"*70
for b in bugsort:
    print "="*50
    print "FAULT #" + str(bugid) + ":",b
    bugids[bugid] = b    
    bugid += 1
    print "FOUND",len(bugs[b]),"TIMES"
    print "FOUND BY",len(set(bugs[b])),"STUDENTS",list(set(bugs[b]))

sfails = {}
sbugs = {}

for s in students:
    for r in allruns:
        if r not in studentruns[s]:
            studentruns[s][r] = []
    sfails[s] = map(len,studentruns[s].values())
    sbugs[s] = map(len,map(set,studentruns[s].values()))

    
studentsort = sorted(students.keys(), key = lambda x:scipy.mean(sbugs[x]),reverse=True)

rank = 1
ranks = {}

for s in studentsort:
    ranks[s] = rank
    rank += 1

rank = 1
tfrank = {}
for s in sorted(students.keys(), key = lambda x:len(set(students[x])), reverse=True):
    tfrank[s] = rank
    rank += 1

rank = 1
tfailrank = {}
for s in sorted(students.keys(), key = lambda x:len(students[x]), reverse=True):
    tfailrank[s] = rank
    rank += 1
    
rank = 1

print "*"*70
for s in studentsort:

    print "#" + str(rank) + ":",s,len(set(students[s])),"FAULTS (#" + str(tfrank[s]) + ") MEAN",round(scipy.mean(sbugs[s]),2),"SD",round(scipy.std(sbugs[s]),2),"/",len(students[s]),"FAILURES (#" + str(tfailrank[s]) + ") MEAN",round(scipy.mean(sfails[s]),2),"SD",round(scipy.std(sfails[s]),2),
    for b in sorted(bugids.keys(),key = int):
        if bugids[b] in students[s]:
            bc = len(filter(lambda x: x == bugids[b], students[s]))
            print "#"+str(b)+":"+str(bc),
    print
    #print "FAILURES: MEAN",scipy.mean(sfails[s]),"SDEV",scipy.std(sfails[s]),"FAULTS: MEAN",scipy.mean(sbugs[s]),"SDEV",scipy.std(sbugs[s])
    for s2 in studentsort:
        if ranks[s] < ranks[s2]:
            p = scipy.stats.ranksums(sbugs[s],sbugs[s2]).pvalue
            if p <= 0.05:
                print "  FAULTS RANK-SUM STATISTICALLY SIGNIFICANTLY BETTER THAN",s2,"(#" + str(ranks[s2]) + ")","p-value =",p
                break
    for s2 in studentsort:
        if  scipy.mean(sfails[s]) > scipy.mean(sfails[s2]): # ranks[s] < ranks[s2]:
            p = scipy.stats.ranksums(sfails[s],sfails[s2]).pvalue
            if p <= 0.05:
                print "  FAILURES RANK-SUM STATISTICALLY SIGNIFICANTLY BETTER THAN",s2,"(#" + str(ranks[s2]) + ")","p-value =",p
                break               
    rank += 1

allTotalBranches = []
allTotalFaults = []
allTotalFailures = []
allMeanFaults = []
allMeanFailures = []
allMeanBranches = []

for s in studentsort:
    allTotalBranches.append(len(sbcov[s]))
    allTotalFaults.append(len(set(students[s])))
    allTotalFailures.append(len(students[s]))
    allMeanFaults.append(scipy.mean(sbugs[s]))
    allMeanFailures.append(scipy.mean(sfails[s]))
    allMeanBranches.append(scipy.mean(bmeans[s]))

print "*" * 70 
print "KENDALL TAU CORRELATIONS:"
print "TOTAL FAULTS VS. TOTAL BRANCHES"
print scipy.stats.kendalltau(allTotalBranches,allTotalFaults)
print "TOTAL FAULTS VS. TOTAL FAILURES"
print scipy.stats.kendalltau(allTotalFailures,allTotalFaults)
print "TOTAL FAULTS VS. MEAN FAULTS"
print scipy.stats.kendalltau(allTotalFaults,allMeanFaults)
print "TOTAL FAULTS VS. MEAN FAILURES"
print scipy.stats.kendalltau(allTotalFaults,allMeanFailures)
print "TOTAL FAULTS VS. MEAN BRANCHES"
print scipy.stats.kendalltau(allTotalFaults,allMeanBranches)
print "TOTAL BRANCHES VS. MEAN BRANCHES"
print scipy.stats.kendalltau(allTotalBranches,allMeanBranches)
print "MEAN FAULTS VS. MEAN BRANCHES"
print scipy.stats.kendalltau(allMeanBranches,allMeanFaults)
print "MEAN FAULTS VS. MEAN FAILURES"
print scipy.stats.kendalltau(allMeanFailures,allMeanFaults)
print "MEAN FAILURES VS. MEAN BRANCHES"
print scipy.stats.kendalltau(allMeanBranches,allMeanFailures)
print "TOTAL FAILURES VS. TOTAL BRANCHES"
print scipy.stats.kendalltau(allTotalBranches,allTotalFailures)
print "TOTAL FAILURES VS. MEAN BRANCHES"
print scipy.stats.kendalltau(allMeanBranches,allTotalFailures)
