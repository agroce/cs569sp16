import glob
import subprocess
import sys

seed = sys.argv[1]

testers = glob.glob("*/tester1.py")
testers.extend (glob.glob("*/*/tester1.py"))

for t in testers:
    student = t.split("/")[0]
    print student,t
    subprocess.call(["cp "+ t + " tester1.py"],shell=True)
    r = subprocess.call(["ulimit -t 25; python tester1.py 20 " + seed + " 100 10 0 1 1 >& " + student + ".z3.20s." + seed + ".tout"],shell=True)
    if r == 152:
        print "TIMEOUT"
        subprocess.call(["echo !TIMEOUT! >> " + student + ".z3.20s." +seed + ".tout"], shell=True)
    elif r != 0: 
        print "CRASHED"
        subprocess.call(["echo !CRASHED! >> " + student + ".z3.20s." +seed + ".tout"], shell=True)        

        
