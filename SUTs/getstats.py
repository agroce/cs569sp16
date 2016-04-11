import scipy
import scipy.stats
import sys

dir = "data/hardout/"

bases = ["seq.2","seq.3","seq.4","rt.10","rt.100","grt.10","grt.100","bfsnovisit"]
bases = ["seq.2","seq.3","seq.4","grt.10","grt.100","bfsnovisit"]
bases = ["seq.2","seq.3","seq.4","grt.100"]
suffix = "hardout"
n = 130

failures = {}
for b in bases:
    failures[b] = []

branches = {}
for b in bases:
    branches[b] = []

statements = {}
for b in bases:
    statements[b] = []

ops = {}
for b in bases:
    ops[b] = []        

for i in xrange(1,n+1):
    for b in bases:
        filename = dir + b + "." + suffix + "." + str(i)
        for l in open (filename):
            ls = l.split()
            if len(ls) > 1:
                if ls[-1] == "FAILED":
                    fails = int(ls[0])
                    if fails > 1:
                        fails = 1
                    failures[b].append(fails)
                if "TSTL BRANCH COUNT" in l:
                    branches[b].append(int(ls[3]))
                if "TSTL STATEMENT COUNT" in l:
                    statements[b].append(int(ls[3]))
                if "TOTAL ACTIONS" in l:
                    ops[b].append(int(ls[2]))
                if "TOTAL TEST OPERATIONS" in l:
                    ops[b].append(int(ls[0]))                    

for b in bases:
    print "======================================================================================"
    print b
    print "FAILURES:",failures[b], "\nMEAN:", scipy.mean(failures[b]), "SDEV:", scipy.std(failures[b])
    print "BRANCHES:",branches[b], "\nMEAN:", scipy.mean(branches[b]), "SDEV:", scipy.std(branches[b])
    print "STATEMENTS:",statements[b], "\nMEAN:", scipy.mean(statements[b]), "SDEV:", scipy.std(statements[b])
    print "ACTIONS:",ops[b],"\nMEAN:", scipy.mean(ops[b]), "SDEV:", scipy.std(ops[b])            

ptarget = 1.0

print
print
print "WILCOX STATISTICAL ANALYSIS WITH P-VALUE TARGET",ptarget

for b1 in bases:
    for b2 in bases:
        if (b1 < b2):
            print "======================================================================================"
            print b1,"VS.",b2
            wfailures = scipy.stats.wilcoxon(failures[b1],failures[b2])[1]
            if wfailures < ptarget:
                print "FAILURES WILCOX:",wfailures
            wbranches = scipy.stats.wilcoxon(branches[b1],branches[b2])[1]
            if wbranches < ptarget:
                print "BRANCHES WILCOX:",wbranches
            wstatements = scipy.stats.wilcoxon(statements[b1],statements[b2])[1]
            if wstatements < ptarget:
                print "STATEMENTS WILCOX:",wstatements
            wops = scipy.stats.wilcoxon(ops[b1],ops[b2])[1]
            if wops < ptarget:
                print "OPERATIONS WILCOX:",wops                
