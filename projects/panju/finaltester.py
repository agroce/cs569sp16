import sut
import random
import sys
import time

# Note, this programe is based on Prof. Alex's bfsrandom
# I combined it with my algorithm to test
#NUM_TESTS = 100

timeout = int(sys.argv[1])
seed = int(sys.argv[2])
depth = int(sys.argv[3])
width = int(sys.argv[4])
faults = int(sys.argv[5])  #write fault
coverage= int(sys.argv[6]) #print internal report
running = int(sys.argv[7]) #print the branch

random.seed(seed)
rgen = random.Random()
rgen.seed(seed)

reducing = 1
GOAL_DEPTH = depth

LAYER_BUDGET = width#BUDGET/GOAL_DEPTH

print "LAYER BUDGET:",LAYER_BUDGET

slack = 0.0
bugs = 0
sut = sut.sut()
sut.silenceCoverage()

sut.restart()

queue = [sut.state()]
visited = []

startALL = time.time()

actCount = 0
elapsed = 0
d = 1

s_dep = 0.15  # sparse depth
s_unit = 0.25  # sparse unit rate

len_dep = int(GOAL_DEPTH * s_dep);
selected_d = [random.randint(0, GOAL_DEPTH) for i in range(1, len_dep)]

fix_blocks = 10;

def binary_srand(len, s_level, min_num): # minimum number: min_num, sparseity level: s_level

    arr = [0]*len;
    sparsity = int(len*s_level);
    if sparsity< min_num:
        sparsity = min_num;

    a = range(len);
    random.shuffle(a);
    sparse_ids = a[0:sparsity]

    for i in sparse_ids:
        arr[i] = 1;

    return arr # return binary arry, in which the non-zero elements corresponding to the state need to take action

def block_rand_ids( n, blk_sparse ):
    block_sz = 0;
    ref_tb = [0]*n; #reference table
    if n>= 20:
        block_sz = int(n/fix_blocks)

        a= range(fix_blocks);
        random.shuffle(a);
        block_ids = a[0:blk_sparse]

        for i in  block_ids:
            start = i*block_sz
            end = (i+1)*block_sz
            ref_tb[start:end] = binary_srand(end - start, 0.5, 2);
    else:# when n< 20
        ref_tb = binary_srand(n,0.5, 1);

    return ref_tb

def about_branch(running, action):
    if running:
        if sut.newBranches() != set([]):
            print "ACTION:", action[0]  # , tryStutter
            for b in sut.newBranches():
                print elapsed, len(sut.allBranches()), "New branch", b
            sawNew = True

        if sut.newStatements() != set([]):
            print "ACTION:", a[0]
            for s in sut.newStatements():
                print elapsed, len(sut.allStatements()), "New statement", s
            sawNew = True
        else:
            sawNew = False



break_count = 0;
fact_cnt =0;
timeout0 = timeout*0.9

while d <= GOAL_DEPTH:
    elapsedALL = time.time() - startALL
    if elapsedALL >= timeout0:
        break

    print "DEPTH",d,"QUEUE SIZE",len(queue),"VISITED SET",len(visited)
    d += 1
    frontier = []
    startLayer = time.time()
    scount = 0

    ref_tb =[1]
    if len(queue)> 1:
        ref_tb = block_rand_ids(len(queue),3)
    for s in queue:
        elapsedALL = time.time() - startALL
        if elapsedALL >= timeout0:
            break

        scount += 1
        sut.backtrack(s)
        allEnabled = sut.enabled()
        random.shuffle(allEnabled)
        #print 'all enabled len', len(allEnabled)
        #print "scount", scount, "len", len(queue)

        for a in allEnabled:
            fact_cnt += 1
            if ref_tb[scount - 1] == 0:
                break_count += 1
                break

            elapsed = time.time() - startLayer
            if elapsed >= LAYER_BUDGET:
                #print 'breaking .....'
                break

            elapsedALL = time.time() - startALL
            if elapsedALL >= timeout0:
                break

            sut.backtrack(s)
            ok = sut.safely(a)
            about_branch(running,a)

            actCount += 1
            if not ok:
                print "FOUND A FAILURE"
                #sut.prettyPrintTest(sut.test())
                print sut.failure()

                if reducing:
                    print "REDUCING"
                    R = sut.reduce(sut.test(), sut.fails, True, True)
                    sut.prettyPrintTest(R)
                print sut.failure()
                if faults:
                    bugs +=1;
                    failname = 'failure' + str(bugs) + '.test'
                    sut.saveTest(R, failname)
                #sys.exit(1)
            s2 = sut.state()

            if s2 not in visited:
                visited.append(s2)
                frontier.append(s2)
            sut.backtrack(s)


    elapsed = time.time() - startLayer
    slack = float(LAYER_BUDGET-elapsed)
    print "SLACK",slack
    if (d < GOAL_DEPTH) and (slack > 0):
        LAYER_BUDGET = LAYER_BUDGET+slack/(GOAL_DEPTH-d)
        print "NEW LAYER BUDGET",LAYER_BUDGET
    queue = frontier

while (time.time() - startALL) <= (timeout):
    sut.restart()
    cnt=1
    for s in xrange(0,depth):
        if (time.time() - startALL) >= (timeout):
            break;

        act = sut.randomEnabled(rgen)
        ok = sut.safely(act)
        cur_state=sut.state()
        actCount+=1
        cnt += 1
        about_branch(running,act)  #print the branch
        if cur_state not in visited:
            visited.append(cur_state)
        if not ok:
            #tuplelist.append((cur_state,cnt))
            print "Note:: There is a Failure"
            if reducing:
                print "Start Reducing"
                Rdc = sut.reduce(sut.test(), sut.fails, True, True)  # find a bug, min size sequence
                sut.prettyPrintTest(Rdc)
            print sut.failure()

            if faults:
                bugs+=1
                failname='failure'+str(bugs)+'.test'
                sut.saveTest(Rdc, failname);
                #for i in range(len(Rdc)):
                #    with open(failname, 'w') as f:
                #        f.write('\n' + 'This is a bug' + str(bugs) + '\n')
                #        f.write(str(sut.failure()) + '\n')
                  #      f.write(str(Rdc) + '\n')
if (coverage):
    sut.internalReport()

print "SLACK",slack
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-startALL
