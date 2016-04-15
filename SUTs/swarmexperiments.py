import subprocess
import sys

def performExperiment(cmd, file, timeout):
    ok = False
    while not ok:
        print cmd,"-->",file
        subprocess.call(["ulimit -t " + str(timeout*2) + ";" + cmd + " >& " + file], shell=True)
        subprocess.call(["grep FAILED " + file],shell=True)
        ok = True

timeout = 120
            
for i in xrange(0,200):
    print "EXPERIMENT",i
    performExperiment("python ~/tstl/generators/randomtester.py --multiple --internal --ignoreprops --timeout " + str(timeout), "noswarm.swarmexp." + str(i), timeout)
    performExperiment("python ~/tstl/generators/randomtester.py --swarm --multiple --internal --ignoreprops --timeout " + str(timeout), "swarm.swarmexp." + str(i), timeout)    



