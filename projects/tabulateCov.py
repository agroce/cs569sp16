import glob
import subprocess
import scipy

testers = []
testers.extend (glob.glob("*/tester1.py"))
testers.extend (glob.glob("*/*/tester1.py"))

printGnuplot = False

data1 = []
data2 = []
data3 = []

n = 0
s = 0
for t in testers:
    s += 1
    student = t.split("/")[0]
    res = sorted(glob.glob(student + "*.tout"))
    for f in res:
        n += 1
        scov = 0
        bcov = 0
        timeout = ""
        crashed = ""
        internalb = "NOBRANCHES"
        internals = "NOSTATEMENTS"        
        for l in open(f):
            if "branch" in l:
                bcov = l.split()[1]
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
        print student,f,"RUNNING:",bcov,"BRANCHES:",internalb,"STATEMENTS:",internals,timeout,crashed
        if printGnuplot:
            print n,s,bcov,"# GNUPLOT"
        if (timeout == "") and (crashed == ""):
            data1.append((f,bcov))
            if internals != "NOSTATEMENTS":
                data2.append((f,internals))
            else:
                data2.append((f,0))
            if internalb != "NOBRANCHES":
                data3.append((f,internalb))
            else:
                data3.append((f,bcov))

print "\n\nSORTED BY BEST BRANCH COVERAGE RUNNING TOTAL"
data1 = sorted(data1,key=lambda p:p[1],reverse=True)

for (s,b) in data1:
    print s,b

print "\n\nSORTED BY BEST TOTAL STATEMENT COVERAGE"
data2 = sorted(data2,key=lambda p:int(p[1]),reverse=True)

for (s,b) in data2:
    print s,b    
            
print "\n\nSORTED BY EITHER BRANCH COVERAGE METHOD"
data3 = sorted(data3,key=lambda p:int(p[1]),reverse=True)

for (s,b) in data3:
    print s,b

print "\n\nMEAN OVER ALL RUNS"
sdata = {}
for (s,b) in data3:
    student = s.split(".")[0]
    if student not in sdata:
        sdata[student] = []
    sdata[student].append(int(b))

data4 = []
for s in sdata:
    data4.append((s,scipy.mean(sdata[s]),len(sdata[s]),scipy.std(sdata[s])))

data4 = sorted(data4,key=lambda p:p[1],reverse=True)
for (s,b,l,sdev) in data4:
    print s,round(b,2),l,round(sdev,2)
