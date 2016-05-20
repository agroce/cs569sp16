import glob
import subprocess
import sys
import shutil

seed = sys.argv[1]
time = sys.argv[2]

testers = glob.glob("*/tester2.py")
testers.extend (glob.glob("*/*/tester2.py"))

timeout = str(int(time)+10)

for t in testers:
    student = t.split("/")[0]
    print student,t
    shutil.copyfile(t,"tester2.py")
    r = subprocess.call(["ulimit -t " + timeout + "; python tester2.py " + time + " " + seed + " 100 10 0 1 1 >& " + student + ".sqlparse." + time + "s." + seed + ".tout"],shell=True)
    if r == 152:
        print "TIMEOUT"
        subprocess.call(["echo !TIMEOUT! >> " + student + ".sqlparse." + time + "s." +seed + ".tout"], shell=True)
    elif r != 0: 
        print "CRASHED"
        subprocess.call(["echo !CRASHED! >> " + student + ".sqlparse." + time + "s." +seed + ".tout"], shell=True)        

        
