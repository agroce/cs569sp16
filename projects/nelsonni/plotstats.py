import scipy
import scipy.stats
import sys
from pylab import *
from matplotlib.backends.backend_pdf import PdfPages

bases = ["final.genetic.out"]

failures = {}
for b in bases:
    failures[b] = []

branches = {}
for b in bases:
    branches[b] = []

statements = {}
for b in bases:
    statements[b] = []    

for b in bases:
    filename = b
    for l in open (filename):
        ls = l.split()
        if len(ls) > 1:
            if ls[-1] == "FAILED":
                failures[b].append(int(ls[0]))
            if "TSTL BRANCH COUNT" in l:
                branches[b].append(int(ls[3]))
            if "TSTL STATEMENT COUNT" in l:
                statements[b].append(int(ls[3]))                    

for b in bases:
    print "======================================================================================"
    print b
    print "FAILURES:",failures[b], "\nMEAN:", scipy.mean(failures[b]), "SDEV:", scipy.std(failures[b])
    print "BRANCHES:",branches[b], "\nMEAN:", scipy.mean(branches[b]), "SDEV:", scipy.std(branches[b])
    print "STATEMENTS:",statements[b], "\nMEAN:", scipy.mean(statements[b]), "SDEV:", scipy.std(statements[b])        

ptarget = 0.50

# print
# print
# print "WILCOX STATISTICAL ANALYSIS WITH P-VALUE TARGET",ptarget

# for b1 in bases:
#     for b2 in bases:
#         if (b1 < b2):
#             print "======================================================================================"
#             print b1,"VS.",b2
#             wfailures = scipy.stats.wilcoxon(failures[b1],failures[b2]).pvalue
#             if wfailures < ptarget:
#                 print "FAILURES WILCOX:",wfailures
#             wbranches = scipy.stats.wilcoxon(branches[b1],branches[b2]).pvalue
#             if wbranches < ptarget:
#                 print "BRANCHES WILCOX:",wbranches
#             wstatements = scipy.stats.wilcoxon(statements[b1],statements[b2]).pvalue
#             if wstatements < ptarget:
#                 print "STATEMENTS WILCOX:",wstatements

                
f1 = figure()

data = []
labels = []
for b in bases:
    data.append(failures[b])
    labels.append(b)

ylabel("# Failures")
boxplot(data,labels=labels)

f2 = figure()

data = []
labels = []
for b in bases:
    data.append(branches[b])
    labels.append(b)

ylabel("Branches")
boxplot(data,labels=labels)

pp = PdfPages("data.pdf")
pp.savefig(1)
pp.savefig(2)
pp.close()
