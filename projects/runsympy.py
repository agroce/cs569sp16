import glob
import subprocess
import sys
import shutil
import os

time = "120"

testers = glob.glob("*/finaltester.py")

timeout = str(int(time)+10)

for s in xrange(1017,1030):
    seed = str(s)
    for t in testers:
        student = t.split("/")[0]
        print student,t
        shutil.copyfile(t,"finaltester.py")
        for f in glob.glob("*.test"):
            subprocess.call(["rm -rf " + f],shell=True)
        subprocess.call(["mkdir sympytests."+ student],shell=True)
        subprocess.call(["mkdir sympytests."+ student + "/" + seed],shell=True)
        if os.path.exists(student + ".sympy." + time + "s." + seed + ".tout"):
            continue
        try:
            r = subprocess.call(["ulimit -t " + timeout + "; python finaltester.py " + time + " " + seed + " 100 10 1 1 1 >& " + student + ".sympy." + time + "s." + seed + ".tout"],shell=True)
        except:
            print "REMOVING LAST PARTIAL RUN"
            os.remove(student + ".sympy." + time + "s." + seed + ".tout")
            raise
        try:
            for f in glob.glob("*.test"):
                subprocess.call(["mv " + f + " sympytests." + student + "/" + seed], shell=True)
            if r == 152:
                print "TIMEOUT"
                subprocess.call(["echo !TIMEOUT! >> " + student + ".sympy." + time + "s." +seed + ".tout"], shell=True)
            elif r != 0: 
                print "CRASHED"
                subprocess.call(["echo !CRASHED! >> " + student + ".sympy." + time + "s." +seed + ".tout"], shell=True)
        except:
            print "INTERRUPTED COPYING TESTS!"
            raise
        
