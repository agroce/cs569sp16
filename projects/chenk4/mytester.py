import sut
import random
import sys
import time
import argparse
from collections import namedtuple


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--depth', type=int, default=100,help='Maximum search depth (100 default).')
    parser.add_argument('-w', '--width', type=int, default=10,help='Maximum memory/BFS queue/other parameter for search width (10 default).')    
    parser.add_argument('-t', '--timeout', type=int, default=30,help='Timeout in seconds (30 default).')
    parser.add_argument('-s', '--seed', type=int, default=None,help='Random seed (default = None).')
    parser.add_argument('-b', '--redestribute', type=int, default=4,help='Redestribute the time for running Radom Test (default = 4).')    
    parser.add_argument('-f', '--faults', action='store_true',help='Save the failure cases.')    
    parser.add_argument('-g', '--reducing', action='store_true',help='reduce -- Do not report full failing test.')  
    parser.add_argument('-r', '--running', action='store_true',help='running info on branch coverage')    
    parser.add_argument('-c', '--coverage', action='store_true',help='Give a final report.')        
    parsed_args = parser.parse_args(sys.argv[1:])
    return (parsed_args, parser)

def make_config(pargs, parser):
    """
    Process the raw arguments, returning a namedtuple object holding the
    entire configuration, if everything parses correctly.
    """
    pdict = pargs.__dict__
    # create a namedtuple object for fast attribute lookup
    key_list = pdict.keys()
    arg_list = [pdict[k] for k in key_list]
    Config = namedtuple('Config', key_list)
    nt_config = Config(*arg_list)
    return nt_config   

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

def main ():
    global sut,depth,width,timeout,redestribute,faults,reducing,running,coverage

    parsed_args, parser = parse_args()
    config = make_config(parsed_args, parser)
    print('Tester using config={}'.format(config))

    depth = config.depth
    width = config.width
    timeout = config.timeout
    rgen = random.Random(config.seed)
    redestibute = config.redestribute
    faults = config.faults
    reducing = config.reducing
    running = config.running
    coverage = config.coverage


    sut = sut.sut()
    sut.silenceCoverage()
    startTM = time.time()
    layer = width
    slack = 0.0
    bugs = 0
    actCount = 0
    elapsed = 0
    queue=[]
    visited = []
    tuplelist=[]
    frontier = []


    print "START PHASE ONE ........\n"
    while (time.time() - startTM) <= (timeout/redestibute):
        sut.restart()
        d1=1
        for s0 in xrange(0,depth): 

            elapsedTM = time.time() - startTM
            if elapsedTM>=(timeout/redestibute):
                break          

            d1+=1
            act = sut.randomEnabled(rgen)
            ok0 = sut.safely(act)
            sstate=sut.state()
            actCount+=1
            branchFun(running,act,0)  #print the branch
            if sstate not in visited:
                visited.append(sstate)
            if not ok0:
                # queue.append(sstate)
                tuplelist.append((sstate,d1))
                print "Note:: There is a Failure"
                # print sut.failure()

                if reducing:            
                    print "Start Reducing"
                    R = sut.reduce(sut.test(),sut.fails, True, True) # find a bug, min size sequence
                    sut.prettyPrintTest(R)

                if faults:
                    bugs+=1
                    failname='failure'+str(bugs)+'.test'
                    sut.saveTest(sut.test(),failname) 

    print "TOTAL RUNTIME Phase 1",time.time()-startTM

    if len(tuplelist) != 0:
        tuplelistnew = sorted(tuplelist,key = lambda x: (x[1])) 
        print len(tuplelistnew ), 'tuplelistnew...............'
        dlist =[]
        for j in xrange (0,len(tuplelistnew)):
            dlist.append(tuplelistnew[j][1])
        print dlist, 'This is the dlist !!!!!!!!!!!!!!!!!!!!'
        
    else:
        sut.restart()
        tuplelistnew =[(sut.state(),1)]


    print "START PHASE TWO ........\n"

    for tl in xrange (0,len(tuplelistnew)):
            elapsedTM = time.time() - startTM
            if elapsedTM>=timeout:
                break  
            d= tuplelistnew[tl][1]
            print tl,d,len(tuplelistnew),'happy..............'
            queue = [tuplelistnew[tl][0]]
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
                        ok = sut.safely(act)
                        branchFun(running,act,1)  

                        actCount += 1  #count all action excuted
                        if not ok:
                            #determine printing of fault
                            print "Note:: There is a Failure"
                            # print sut.failure()

                            if reducing:            
                                print "Start Reducing"
                                R = sut.reduce(sut.test(),sut.fails, True, True) # find a bug, min size sequence
                                sut.prettyPrintTest(R)

                            if faults:
                                bugs+=1
                                failname='failure'+str(bugs)+'.test'
                                sut.saveTest(sut.test(),failname) 
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

    # print "TOTAL ACTIONS",actCount
    print "TOTAL RUNTIME",time.time()-startTM

if __name__ == '__main__':
    main()    
