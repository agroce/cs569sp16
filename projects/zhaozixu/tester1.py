import sut as SUT

import sys
import time
import random
import argparse

def parse_args():
    args = {}
    args['timeout']=int(sys.argv[1])
    args['seed']=int(sys.argv[2])
    args['depth']=int(sys.argv[3])
    args['width']=int(sys.argv[4])
    if sys.argv[5] == "0":
        args['faults'] = False
    elif sys.argv[5] == "1":
        args['faults'] = True
    else:
        sys.exit("ERROR: FAULTS ARGUMENT INVALID. ABORT SYSTEM.")
    if sys.argv[6] == "0":
        args['cover'] = False
    elif sys.argv[6] == "1":
        args['cover'] = True
    else:
        sys.exit("EERROR: COVER ARGUMENT INVALID. ABORT SYSTEM.")
    if sys.argv[7] == "0":
        args['running'] = False
    elif sys.argv[7] == "1":
        args['running'] = True
    else:
        sys.exit("ERROR: RUNNING ARGUMENT INVALID. ABORT SYSTEM.")
    print "TIMEOUT=", args['timeout'], ", SEED=", args['seed'], ", DEPTH=", args['depth'], ", WIDTH=", args['width'], ", FAULTS=", args['faults'], ", COVER=", args['cover'], ", RUNNING=", args['running'] 
    
    return args

#initilize all variable for severals
def init_com_pool(sut, rand):
    com_pool = []
    actions = sut.enabled()
    init_num = rand.randint(1, len(actions))
    flag = True
    while len(com_pool) < init_num:
        #print len(com_pool), len(actions)
        sut.restart()
        while flag == True:
            action = sut.randomEnabled(rand)
            #may need exceptions
            sut.safely(action)
            #print "action in ", action in actions
            if action in actions:   
                pass
            else:
                flag = False
                #print "flag", flag
            #print "End"
        flag = True
        if sut.test() not in com_pool:
            com_pool.append(sut.test())
        #print "##############################", len(com_pool)
    
    return com_pool

def random_seq(seqs, rand, n):
    seq = []
    while len(seq) < n:
        if len(seqs) == 1:
            p = 0
        elif len(seqs) == 0:
            break
        else:
            p = rand.randint(0, len(seqs)-1)
        #print seqs[p], len(seq)
        if seqs[p] not in seq:
            seq = seq + seqs[p]
    return seq
             
#check
#check dependency to see whether we properly initialized    
#def check_dependency(action):
    
    
#check variables   
#def check_variables():
    
#check exceptions
#def isException():
    
    
#def isRedundent(sut, seq):
    #variable status is not none
    
    #repeat same actions


args = parse_args()
sut = SUT.sut()

rand = random.Random(args['seed'])
depth = []

#store the component for test generation. Initilized by all the enabled actions first. This means we can initialize all varible first.
com_pool = init_com_pool(sut, rand)

vars_num = len(com_pool[0])
#initialized empty
bad_pool = []
nice_pool = []
#print com_pool


start = time.time()
while time.time() - start < args['timeout']:
    sut.restart()
    
    #which way to increase
    which = rand.randint(1,2)
    if which == 1:
        test = random_seq(com_pool, rand, rand.randint(2, 50))
        fc = sut.failsCheck(test)
        if sut.test() not in nice_pool and sut.test() not in bad_pool:
            if not fc:
                com_pool.append(sut.test())
                nice_pool.append(sut.test())
            else:
                bad_pool.append(sut.test())
                if args['faults']:
                    sut.prettyPrintTest(sut.test())
    else:
        test = com_pool[rand.randint(0, len(com_pool)-1)]
        ok = sut.failsCheck(test)
        action = sut.randomEnabled(rand)
        ok = sut.safely(action) 
        if sut.test() not in nice_pool and sut.test() not in bad_pool:
            if ok:
                com_pool.append(sut.test())
                nice_pool.append(sut.test())
            else:
                bad_pool.append(sut.test())
                if args['faults']:
                    sut.prettyPrintTest(sut.test())
    #print "1111111111111111111111111111111111111111111111111"
    sut.saveTest(sut.test(), "out.txt")
    if args['running']:
        if sut.newBranches() != set([]):
            for b in sut.newBranches():
                print (time.time() - start),len(sut.allBranches()),"New branch",b
duration = (time.time() - start)

print "Producing Report..."

print"##########################  TEST REPORT  ##########################"
print "TEST DURATION:", duration
if args['faults']:
    print len(bad_pool), "FAILED"
if args['cover']:
    sut.internalReport()
print"###################################################################"
#print com_pool
