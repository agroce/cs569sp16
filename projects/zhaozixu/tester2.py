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
    init_num = rand.randint(1, 10)
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
            com_pool.append(sut.state())
        #print "##############################", len(com_pool)
    
    return com_pool
    
def handle_failure(sut, fault_pool):
    size = len(fault_pool[0])
    k = 0
    for f in fault_pool:
        k += 1
        sut.restart()
        sut.failsCheck(f[size-1])
        sut.reduce(sut.test(), sut.fails)
        
        f = open("failure.test", 'a')
        f.write("\\\\\\\\\\FAILURE NO." + str(k) + "\\\\\\\\\\\n")
        f.write("FAILURE INFO:\n")
        f.write(str(sut.failure()) + "\n")
        f.write("WARNING INFO:\n")
        f.write(str(sut.warning()) + "\n")
        f.write("STEPS TRACE:\n")
        for t in sut.test():
            f.write(sut.serializable(t) + "\n")
        f.write("\\\\\\\\\\END FAILURE NO." + str(k) + "\\\\\\\\\\\n\n\n\n\n")
        f.close()
        


#initialize and pass arguments
args = parse_args()

#initialize sut object
sut = SUT.sut()

#initialize random object
rand = random.Random(args['seed'])

#initialize the pool to store test state
pass_pool = init_com_pool(sut, rand)
fault_pool = []

#begin test
start = time.time()
while time.time() - start < args['timeout']:
    sut.restart()
    ok = True
    #pick up one sequence
    size = len(pass_pool)
    
    #pick up proper sequence
    depthOK = True
    while depthOK:
        if size > 0:
            test = random.choice(pass_pool)
            if len(test[len(test)-1]) < args['depth']:
                sut.backtrack(test)
                break
        
    #increase sequence 
    actions = sut.randomEnableds(rand, random.randint(1, len(sut.enabled())))
    for act in actions:
        ok = sut.safely(act)
        prop = sut.check()
    
        if not ok or not prop:
            fault_pool.append(sut.state())
            break
            
        if args['running']:
            if sut.newBranches() != set([]):
                print "ACTION:", act[0]
                for b in sut.newBranches():
                    print (time.time() - start),len(sut.allBranches()),"New branch",b
        
        #if current test depth is longer than parsed depth, stop
        if len(sut.test()) == args['depth']:
            break
            
    if ok and prop:    
        pass_pool.append(sut.state())

duration = (time.time() - start)
print "\n\n\nProducing Report...\n\n\n"

print"##########################  TEST REPORT  ##########################"
print "TEST DURATION:", duration
if args['faults']:
    print len(fault_pool), "FAILED"
    if len(fault_pool) > 0:
        handle_failure(sut, fault_pool)
        print "OUTPUT TEST REPORT"
    
if args['cover']:
    sut.internalReport()
print"###################################################################"    
#for s in pass_pool:
#    print s
    


