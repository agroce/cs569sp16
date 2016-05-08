import glob
import subprocess
import sys
import shutil

seed = sys.argv[1]

testers = glob.glob("*/tester1.py")
testers.extend (glob.glob("*/*/tester1.py"))


for t in testers:
    student = t.split("/")[0]
    print student,t
    shutil.copyfile(t,"tester1.py")
    r = subprocess.call(["ulimit -t 45; python tester1.py 40 " + seed + " 100 10 0 1 1 >& " + student + ".avl.40s." + seed + ".tout"],shell=True)
    if r == 152:
        print "TIMEOUT"
        subprocess.call(["echo !TIMEOUT! >> " + student + ".avl.40s." +seed + ".tout"], shell=True)
    elif r != 0: 
        print "CRASHED"
        subprocess.call(["echo !CRASHED! >> " + student + ".avl.40s." +seed + ".tout"], shell=True)        

        
