import sut as SUT

import sys
import time
import random
import argparse
from collections import namedtuple

def parse_args():
	parser = argparse.ArgumentParser()

	parser.add_argument('-t', '--timeout', type=int, default=60, help='Timeout in seconds (default = 60).')
	parser.add_argument('-s', '--seed', type=int, default=10, help='Random seed (default = 10).')
	parser.add_argument('-d', '--depth', type=int, default=100, help='Maximum length of a sequence (default = 100).')
	parser.add_argument('-w', '--width', type=int, default=10, help='(This is not used. Just keep remained)).')
	parser.add_argument('-l', '--length', type=int, default=20, help='Maximum increased length of a sequence (default = 20. Recommand: Better in range of 10 and 200).')
	parser.add_argument('-f', '--faults', action='store_true', help='Store failure information (default = False).')
	parser.add_argument('-c', '--coverage', action='store_true', help='Produce a coverage report at the end (default = False).')
	parser.add_argument('-r', '--running', action='store_true', help='Produce a running brach coverage report at the end(default = False).')
    
	parsed_args = parser.parse_args(sys.argv[1:])

	return (parsed_args, parser)


def make_config(pargs, parser):
	pdict = pargs.__dict__
	key_list = pdict.keys()
	arg_list = [pdict[k] for k in key_list]
	Config = namedtuple('Config', key_list)
	nt_config = Config(*arg_list)
	return nt_config

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
parsed_args, parser = parse_args()
config = make_config(parsed_args, parser)
print('Feedback Testing using config={}'.format(config))
#initialize sut object
sut = SUT.sut()

#initialize random object
rand = random.Random(config.seed)

#best way to store it is to be like this: {[poolUses]:sut.state()}
passPool = []
passPool.append(sut.state())

faultPool = []

b = 0
start = time.time()
while time.time() - start < config.timeout:
    sut.restart()
    
    sut.backtrack(random.choice(passPool))
    zero = sut.enabled()
    
    i = 0
    action = sut.randomEnabled(rand)
    nums = random.randint(1, config.length)
    safe = None
    prop = None
    while i<nums:
        safe = sut.safely(action)
        prop = sut.check()
        
        if config.running:
            if sut.newBranches() != set([]):
                print "ACTION:", action[0]
                for b in sut.newBranches():
                    print (time.time() - start),len(sut.allBranches()),"New branch",b
        
        if not safe or not prop:
            faultPool.append(sut.state())
            break
            
        if (time.time() - start) >= config.timeout:
            print "TIMEOUT. TERMINATED."
            break
            
        #if current test depth is longer than parsed depth, stop
        if len(sut.test()) >= config.depth:
            break
        
        first = list(set(sut.enabled())-set(zero))
        if len(first) > 0:
            action = random.choice(first)
        else:
            action = sut.randomEnabled(rand)
        zero = sut.enabled()
        i += 1
            
    if (time.time() - start) >= config.timeout:
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
if config.faults:
    print len(faultPool), "FAILED TEST"
    if len(faultPool) > 0:
        handleFailure(sut, faultPool)
        print "OUTPUT FAILURE TEST REPORT"
    
if config.coverage:
    sut.internalReport()
print"###################################################################" 
    
        
    
    

