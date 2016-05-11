import glob
import subprocess
import sys
import shutil

seed = sys.argv[1]
time = sys.argv[2]

testers = glob.glob("*/tester1.py")
testers.extend (glob.glob("*/*/tester1.py"))

timeout = str(int(time)+5)

for t in testers:
    student = t.split("/")[0]
    print student,t
    shutil.copyfile(t,"tester1.py")
    r = subprocess.call(["ulimit -t " + timeout + "; python tester1.py " + time + " " + seed + " 100 10 0 1 1 >& " + student + ".avl." + time + "s." + seed + ".tout"],shell=True)
    if r == 152:
        print "TIMEOUT"
        subprocess.call(["echo !TIMEOUT! >> " + student + ".avl." + time + "s." +seed + ".tout"], shell=True)
    elif r != 0: 
        print "CRASHED"
        subprocess.call(["echo !CRASHED! >> " + student + ".avl." + time + "s." +seed + ".tout"], shell=True)        

        
