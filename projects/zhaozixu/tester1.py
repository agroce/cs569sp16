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
    if sys.argv[5] == "0":
        args['running'] = False
    elif sys.argv[5] == "1":
        args['running'] = True
    else:
        sys.exit("ERROR: RUNNING ARGUMENT INVALID. ABORT SYSTEM.")
    print "TIMEOUT=", args['timeout'], ", SEED=", args['seed'], ", DEPTH=", args['depth'], ", WIDTH=", args['width'], ", FAULTS=", args['faults'], ", COVER=", args['cover'], ", RUNNING=", args['running'] 
    
    return args
    
#randomly generate a new sequence
def random_seq(seqs, rgen, n):
    seq = ()
    while len(seq) < n:
        if len(seqs) == 1:
            p = 0
        elif len(seqs) == 0:
            break
        else:
            p = rgen.randint(0, len(seqs)-1)
        print seqs[p], len(seq)
        if (len(seqs[p]) == 3) and isinstance(seqs[p][0], basestring):
            seq = seq, seqs[p]
        else:
            seq = seq + seqs[p]
    if cmp(seq[0], ()) == 0:
        return seq[1:]
    return seq

args = parse_args()
sut = SUT.sut()

rgen = random.Random()
bugs = 0

##find a way to identify the variable or method and input to the com_pool first
com_pool = sut.enabled()
bad_pool = []
exc_pool = []
nice_pool = []

start = time.time()
while time.time() - start < args['timeout']:
    sut.restart()
    seqs = random_seq(com_pool, rgen, 2)
    
    for i in range(0, len(seqs)):
        action = seqs[i]
        ok = sut.safely(action)
        if ok == False or sut.check() == False:
            bad_pool.append(seqs)
            bugs += 1
            print "APPEND BAD SEQUENCE"
            print sut.failure()
            continue
    #filter part, not success yet
    
    #ok, then we can output good sequence
    nice_pool.append(seqs)
    com_pool.append(seqs)
    print "APPEND GOOD SEQUENCE"
            

duration = (time.time() - start)

print"####################TEST REPORT####################"
print "TEST DURATION", duration
if args['faults'] == True:
    print bugs, "FAILED"
if args['cover']:
    sut.internalReport()
print"###################################################"
#print com_pool
