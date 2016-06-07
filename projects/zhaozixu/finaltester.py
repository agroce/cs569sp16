import sut as SUT

import re
import sys
import time
import random
import argparse

def parseArgs():
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

def handleFailure(sut, faultPool):
    size = len(faultPool[0])
    k = 0
    temp = []
    for f in faultPool:
        k += 1
        sut.restart()
        sut.failsCheck(f[size-1])
        sut.reduce(sut.test(), sut.fails)
        filename = 'failure'+str(k)+'.test'
        sut.saveTest(sut.test(), filename)
        
#        f = open("failure.test", 'a')
#        f.write("\\\\\\\\\\FAILURE NO." + str(k) + "\\\\\\\\\\\n")
#        f.write("FAILURE INFO:\n")
#        f.write(str(sut.failure()) + "\n")
#        f.write("WARNING INFO:\n")
#        f.write(str(sut.warning()) + "\n")
#        f.write("STEPS TRACE:\n")
#        for t in sut.test():
#            f.write(sut.serializable(t) + "\n")
#        f.write("\\\\\\\\\\END FAILURE NO." + str(k) + "\\\\\\\\\\\n\n\n\n\n")
#        f.close()
        


#initialize and pass arguments
args = parseArgs()

#initialize sut object
sut = SUT.sut()

#initialize random object
rand = random.Random(args['seed'])


#best way to store it is to be like this: {[poolUses]:sut.state()}
passPool = []
passPool.append(sut.state())
faultPool = []

b = 0
start = time.time()
while time.time() - start < args['timeout']:
    sut.restart()
    
    sut.backtrack(random.choice(passPool))
    zero = sut.enabled()
    
    i = 0
    action = sut.randomEnabled(rand)
    nums = random.randint(1, 20)
    safe = None
    prop = None
    while i<nums:
        safe = sut.safely(action)
        prop = sut.check()
        
        if args['running']:
            if sut.newBranches() != set([]):
                print "ACTION:", action[0]
                for b in sut.newBranches():
                    print (time.time() - start),len(sut.allBranches()),"New branch",b
        
        if not safe or not prop:
            faultPool.append(sut.state())
            break
        
        if (time.time() - start) >= args['timeout']:
            print "TIMEOUT. TERMINATED."
            break
        
        #if current test depth is longer than parsed depth, stop
        if len(sut.test()) >= args['depth']:
            break
        
        first = list(set(sut.enabled())-set(zero))
        if len(first) > 0:
            action = random.choice(first)
        else:
            action = sut.randomEnabled(rand)
        zero = sut.enabled()
        i += 1
    
    if (time.time() - start) >= args['timeout']:
        print "TIMEOUT. TERMINATED."
        break
            
    if safe and prop:    
        passPool.append(sut.state())
        #filename = 'case'+str(b)+'.test'
        #sut.saveTest(sut.test(), filename)
        #b += 1
        
duration = (time.time() - start)
print "\n\n\nProducing Report...\n\n\n"

print"##########################  TEST REPORT  ##########################"
print "TEST DURATION:", duration
if args['faults']:
    print len(faultPool), "FAILED"
    if len(faultPool) > 0:
        handleFailure(sut, faultPool)
        print "OUTPUT TEST REPORT"
    
if args['cover']:
    sut.internalReport()
print"###################################################################" 
    
        
    
    




