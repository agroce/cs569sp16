import subprocess
import sys

for i in xrange(100,200):
    print "EXPERIMENT",i
#    subprocess.call(["python bfsrandom.py >& bfs.hardout."+ str(i)], shell=True)
    #subprocess.call(["python bfsnovisited.py >& bfsnovisit.hardout."+ str(i)], shell=True)
    subprocess.call(["python rtSeqs.py 2 >& seq.2.hardout."+ str(i)], shell=True)
    subprocess.call(["python rtSeqs.py 3 >& seq.3.hardout."+ str(i)], shell=True)
    subprocess.call(["python rtSeqs.py 4 >& seq.4.hardout."+ str(i)], shell=True)            
    #subprocess.call(["python ~/tstl/generators/randomtester.py --timeout 300 --depth 10 --multiple --internal >& rt.10.hardout."+ str(i)], shell=True)
    #subprocess.call(["python ~/tstl/generators/randomtester.py --timeout 300 --depth 100 --multiple --internal >& rt.100.hardout."+ str(i)], shell=True)        
    subprocess.call(["python ~/tstl/generators/randomtester.py --timeout 300 --depth 10 --multiple --internal --ignoreprops >& grt.10.hardout."+ str(i)], shell=True)
    subprocess.call(["python ~/tstl/generators/randomtester.py --timeout 300 --depth 100 --multiple --internal --ignoreprops >& grt.100.hardout."+ str(i)], shell=True)
    subprocess.call(["git add *.hardout." + str(i)], shell=True)
    subprocess.call(['git commit -m "More experiments"'], shell=True)
    subprocess.call(['git push'], shell=True)             
