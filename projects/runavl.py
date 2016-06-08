import glob
import subprocess
import sys
import shutil

seed = sys.argv[1]
time = sys.argv[2]

testers = glob.glob("*/tester2.py")

timeout = str(int(time)+5)

for t in testers:
    student = t.split("/")[0]
    print student,t
    shutil.copyfile(t,"tester2.py")
    for f in glob.glob("*.test"):
        subprocess.call(["rm -rf " + f],shell=True)
    subprocess.call(["mkdir tests."+ student],shell=True)
    r = subprocess.call(["ulimit -t " + timeout + "; python tester2.py " + time + " " + seed + " 100 10 1 1 1 >& " + student + ".avl." + time + "s." + seed + ".tout"],shell=True)
    for f in glob.glob("*.test"):
        subprocess.call(["mv " + f + " tests." + student], shell=True)
    if r == 152:
        print "TIMEOUT"
        subprocess.call(["echo !TIMEOUT! >> " + student + ".avl." + time + "s." +seed + ".tout"], shell=True)
    elif r != 0: 
        print "CRASHED"
        subprocess.call(["echo !CRASHED! >> " + student + ".avl." + time + "s." +seed + ".tout"], shell=True)        

        
