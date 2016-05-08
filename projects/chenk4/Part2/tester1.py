import sut
import random
import sys
import time

# python2.7 tester1.py 30 1 100 1 0 1 1
timeout = int(sys.argv[1])
seed = int(sys.argv[2])
depth = int(sys.argv[3])  
width = int(sys.argv[4])   
faults = int(sys.argv[5])  #write fault
coverage= int(sys.argv[6]) #print internal report
running = int(sys.argv[7]) #print the branch

# timeout = 60
# seed = 1
# depth = 40
# width = 1
# fault = 1
# coverage = 1
# running = 1


rgen = random.Random(seed)

layer = width

slack = 0.0
bugs = 0
actCount = 0
elapsed = 0

sut = sut.sut()
sut.silenceCoverage()

# sut.restart()
startTM = time.time()
# queue = [sut.state()]
queue=[]
visited = []
vistedRandom=[]
frontier = []


def branchFun(running,possible,elapsed):
    if  running:
        if sut.newBranches() != set([]):
            print "ACTION:",possible[0]
            for b in sut.newBranches():
                print elapsed,len(sut.allBranches()),"New branch",b
            sawNew = True
        else:
            sawNew = False
        if sut.newStatements() != set([]):
            print "ACTION:",possible[0]
            for s in sut.newStatements():
                print elapsed,len(sut.allStatements()),"New statement",s
            sawNew = True
        else:
            sawNew = False

print "START PHASE ONE ........\n"

while (time.time() - startTM) <= (timeout/20):
    sut.restart()
    for s0 in xrange(0,depth):
        act = sut.randomEnabled(rgen)
        ok0 = sut.safely(act)
        sstate=sut.state()
        actCount+=1
        branchFun(running,act,0)  #print the branch
        if sstate not in visited:
            visited.append(sstate)
        if not ok0:
            queue.append(sstate)
            print "Note:: There is a Failure"
            print "Start Reducing"
            R = sut.reduce(sut.test(),sut.fails, True, True) # find a bug, min size sequence
            sut.prettyPrintTest(R)
            print sut.failure()
            if faults:
                bugs+=1
                failname='failure'+str(bugs)+'.test'
                for i in range(len(R)):
                    with open(failname,'w') as f:
                        f.write('\n'+'This is a bug'+str(bugs)+'\n')                          
                        f.write(str(sut.failure())+'\n')
                        f.write(str(R)+'\n')   

if  len(queue)==0:
    sut.restart()
    queue = [sut.state()]

print "START PHASE TWO ........\n"

d = 1
while d <= depth:
    elapsedTM = time.time() - startTM
    if elapsedTM>=timeout:
        break  

    print "DEPTH",d,"QUEUE SIZE",len(queue),"VISITED SET",len(visited)
    d += 1
    start = time.time()
    scount = 0
    max=0

    # first cycle
    for s in queue:

        elapsedTM = time.time() - startTM
        if elapsedTM>=timeout:
            break  

        scount += 1
        sut.backtrack(s)
        possible = sut.enabled()  # past guard action. enable: name guard act
        rgen.shuffle(possible)
        
        pos=len(possible)  #calculate # of children
        poslist=[]

        #second cycle
        for act in possible:
            elapsedTM = time.time() - startTM
            if elapsedTM>=timeout:
                break   
            elapsed = time.time() - start
            if (elapsed >= layer):
                break   
  
            if len(sut.newStatements()) != 0:
                print "NEW STATEMENTS DISCOVERED",sut.newStatements()   
            if len(sut.newBranches()) != 0:
                print "NEW STATEMENTS DISCOVERED",sut.newStatements() 
            branchFun(running,possible,1)                 
                                
            ok = sut.safely(act)

            actCount += 1  #count all action excuted
            if not ok:
                #determine printing of fault
                print "Note:: There is a Failure"
                print "Start Reducing"
                R = sut.reduce(sut.test(),sut.fails, True, True) # find a bug, min size sequence
                sut.prettyPrintTest(R)
                print sut.failure()
                if faults:
                    bugs+=1
                    failname='failure'+str(bugs)+'.test'
                    for i in range(len(R)):
                        with open(failname,'w') as f:
                            f.write('\n'+'This is a bug'+str(bugs)+'\n')                          
                            f.write(str(sut.failure())+'\n')
                            f.write(str(R)+'\n')    
                #sys.exit(1)  # quit the program
            ss = sut.state()
            if ss not in visited:
                visited.append(ss)
                poslist.append(ss)
            sut.backtrack(s)
        # find the longest children list 
        if (pos > max):
            max = pos  #update max value
            frontier = []
            for k in poslist:
                frontier.insert(0,k)         
        #######
        if (elapsed >= layer):
            print "Note: No Expand",len(queue)-scount
            break

    elapsed = time.time() - start
    slack = float(layer-elapsed)
    print "SLACK",slack
    if (d < depth) and (slack > 0):
        layer = layer+slack/(depth-d)
        print "NEW LAYER BUDGET", layer
    queue = frontier
    
if coverage:
    sut.internalReport()

print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-startTM
