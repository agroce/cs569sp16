import sut
import random
import sys
import time


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


rgen = random.Random()
rgen.seed(seed)

layer = width

slack = 0.0

sut = sut.sut()
sut.silenceCoverage()

sut.restart()
startTM = time.time()
queue = [sut.state()]
visited = []
frontier = []

actCount = 0
elapsed = 0


def branchFun(running,possible):
    if (running):
        if sut.newBranches() != set([]):
            print "Action:", possible[0]
            for b in sut.newBranches():
                print elapsed,len(sut.allBranches()),"New branch",b
            sawNew=True
        else:
            sawNew=False    

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
   
            branchFun(running,possible)                  
            ok = sut.safely(act)

            actCount += 1  #count all action excuted
            if not ok:
                #determine printing of fault
                if (faults):
                    print "Note:: There is a Failure"
                    print "Start Reducing"
                    R = sut.reduce(sut.test(),sut.fails, True, True) # find a bug, min size sequence
                    sut.prettyPrintTest(R)
                    print sut.failure()
                    with open('faults1.test','a') as f:
                        f.write(str(sut.failure))
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
    
if (coverage):
    sut.internalReport()

print "SLACK",slack
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-startTM
