#******** This code is based on the code writing by Pro. Alex in the class and randomtester.py *********

import sut
import random
import sys
import time

"""
def mutate(test):
    tcopy = list(test)
    i = rgen.randint(0,len(tcopy))
    sut.replay(tcopy)
    e = sut.randomEnabled(rgen)
    sut.safely(e)
    trest = [e]
    for s in tcopy[i+1:]:
        if s[1]():
            trest.append(s)
            sut.safely(s)
    tcopy = test[:i]+trest
   
"""  
 
timeout = int(sys.argv[1])
seed = int(sys.argv[2])
depth = int(sys.argv[3])
width = int(sys.argv[4])
faults = int(sys.argv[5])
coverage = int(sys.argv[6])
running = int(sys.argv[7])    

actCount = 0
bugs = 0
no_tests = 0
i = 0

covCount = {}
leastCov = None
savedTest = None

sut = sut.sut()

rgen = random.Random(seed)

start = time.time()
while time.time()-start < timeout:
    for ts in xrange(0,width):
        sut.restart()
        no_tests += 1
        if (savedTest != None) and (rgen.random() > 0.8):
           sut.backtrack(savedTest)
        
        """
        else:
            sut.restart()
            
        if (savedTest != None) and (rgen.random() > 0.5):    
            mutate(sut.test())                       
                            
        """  
        test = False    
        for s in xrange(0,depth):
            act = sut.randomEnabled(rgen)
            ok = sut.safely(act)
            #propok = sut.check()   
            if len(sut.newBranches()) > 0:
                savedTest = sut.state()
                test = True
                
            if (not test) and (leastCov != None) and (leastCov in sut.currBranches()):
                savedTest = sut.state()
                test = True
            actCount += 1
            
            #if running=1, print elapsed time, total brach count, new branch if running=0 don't print
            if running == 1:
                if sut.newBranches() != set([]):
                    print "ACTION:",act[0]
                    for b in sut.newBranches():
                        print time.time() - start,len(sut.allBranches()),"New branch",b
            
            #if faults=1, check for bugs and store them in files, if faults=0 don't check for bugs.
            #if faults == 1:
                #if not ok or not propok:
            if not ok and faults == 1:
                print "FAILURE FOUND.....FAILURES ARE STORING IN FILES"
                i += 1
                bugs += 1
                saveFault = 'failure' + str(bugs) + '.test' 
                sut.saveTest(sut.test(), saveFault)
                print "Number bugs found is" ,i
                sut.restart()   
	            
                """     
                    saveFault = 'failure' + str(bugs) + '.test'
                    file = open(saveFault, 'w')
                    print >> file, "Faults: ", fault,"\n"	
                    print >> file, "Test Cases: "
	            for t in sut.test():
	                print >> file, sut.serializable(t)
	            file.close()
	            """ 
        #To see what is the least covered branch to do experiments on them  
        for s in sut.currBranches():
            if s not in covCount:
                covCount[s] = 0
            covCount[s] += 1    
            sortedCov = sorted(covCount.keys(), key=lambda x: covCount[x])
            leastCov = sortedCov[0]
        
        if (time.time() - start > timeout):
            break    

#Take the name of all actions and sort them by their action count
sortedCov = sorted(covCount.keys(), key=lambda x: covCount[x])

"""
graph = open('covCount.data','w')
n=0
for s in sortedCov:
    print s, covCount[s]
    graph.write(str(n)+"  " + str(covCount[s])+"\n")
    n += 1
graph.close

""" 

# if coverage = 1, print internal report            
if coverage == 1:
    sut.internalReport()
    
print "TOTAL NUMBER OF BUGS",bugs
print "TOTAL NUMBER OF TESTS",no_tests
print "TOTAL NUMBER OF ACTIONS",actCount
print "TOTAL NUMBER OF RUNTIME",time.time()-start