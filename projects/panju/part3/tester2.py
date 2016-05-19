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

GOAL_DEPTH = depth
#BUDGET = 5.0

LAYER_BUDGET = width#BUDGET/GOAL_DEPTH

print "LAYER BUDGET:",LAYER_BUDGET

slack = 0.0

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
blk_sparse = 3;
lg_blk_sparse = 5;
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

def block_rand_ids( n ):
    block_sz = 0;
    ref_tb = [0]*n; #reference table
    if n>= 30:
        block_sz = int(n/fix_blocks)

        a= range(fix_blocks);
        random.shuffle(a);

        # when block size is not big enough >30 < 80
        block_ids = a[0:lg_blk_sparse]
        if n>= 99:
            block_ids = a[0:blk_sparse]

        for i in  block_ids:
            start = i*block_sz
            end = (i+1)*block_sz
            ref_tb[start:end] = binary_srand(end - start, 0.5, 2);

    else:# when n< 30
        ref_tb = binary_srand(n,0.5, 1);

    return ref_tb

block_num = 20; # temporally set the block_Num = 20
def block_shuffle(actions):
    len_ = len(actions)
    block_sz = int(len_/block_num)
    last_blsz = len_ - block_sz *(len_-1);

    a = range(block_num);
    random.shuffle(a);
    newActions = actions;

    cnt = 0;
    for i in a:
        cnt += 1;
        if cnt == block_num:
            break;

        start = i*block_sz;
        end = (i+1)*block_sz;

        nstart = (cnt-1)*block_sz;
        nend = cnt*block_sz;

        newActions[nstart:nend] = actions[start:end]


    start  = a[block_num-1]*block_sz;
    end = start + last_blsz;
    nstart = (cnt - 1) * block_sz;
    nend = nstart + last_blsz
    newActions[nstart:nend] = actions[start:end]

    return newActions



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
while d <= GOAL_DEPTH:
    elapsedALL = time.time() - startALL
    if elapsedALL >= timeout:
        break

    print "DEPTH",d,"QUEUE SIZE",len(queue),"VISITED SET",len(visited)
    d += 1
    frontier = []
    startLayer = time.time()
    scount = 0

    ref_tb =[1]
    if len(queue)> 1:
        ref_tb = block_rand_ids(len(queue))
    for s in queue:
        elapsedALL = time.time() - startALL
        if elapsedALL >= timeout:
            break

        scount += 1

        sut.backtrack(s)
        allEnabled = sut.enabled()
        if len(allEnabled)<40:
            random.shuffle(allEnabled)
        else:
            allEnabled = block_shuffle(allEnabled)

        # do a nest inside allEnabled


        if ref_tb[scount - 1] == 0:
            #break_count += 1
            continue

       # ref_tb_act = [1]
       # local_actcnt = 0;
        #if len(allEnabled)>1:
        #    ref_tb_act = block_rand_ids(len(allEnabled))
       # print "len of allenabled", len(allEnabled )
        local_cnt =0;
        for a in allEnabled:
            #if local_cnt >20 and local_cnt >= 0.4*len(allEnabled):
            #    continue;

            elapsed = time.time() - startLayer
            if elapsed >= LAYER_BUDGET:
                #print 'breaking .....'
                break

            elapsedALL = time.time() - startALL
            if elapsedALL >= timeout:
                break

            sut.backtrack(s)
            ok = sut.safely(a)
            about_branch(running,a)

            actCount += 1
            if not ok:
                print "FOUND A FAILURE"
                #sut.prettyPrintTest(sut.test())
                print sut.failure()
                print "REDUCING"
                R = sut.reduce(sut.test(),sut.fails, True, True)
                sut.prettyPrintTest(R)
                print sut.failure()
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

if (coverage):
    sut.internalReport()

print "SLACK",slack
print "TOTAL ACTIONS",actCount
print "TOTAL RUNTIME",time.time()-startALL
