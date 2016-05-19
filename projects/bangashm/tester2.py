import sut as SUT
import random
import time
import sys
import argparse
from collections import namedtuple

def make_config(pargs, parser):
    pdict = pargs.__dict__
    key_list = pdict.keys()
    arg_list = [pdict[k] for k in key_list]
    Config = namedtuple('Config', key_list)
    nt_config = Config(*arg_list)
    return nt_config

def check_action():
    global num, actioncount
    action = sut.randomEnabled(R)
    actioncount +=1
    ok = sut.safely(action)
    elapsed = time.time() - start
    if config.running:
        if len(sut.newBranches()) > 0:
            print "Action count:", action[0]
            for b in sut.newBranches():
                print elapsed, len(sut.allBranches()),"New branch",b
    
    if not ok:
        num += 1
        print "Bug Found" , num
        print "Shrinking now"
        startReduce = time.time()
        test = sut.reduce(sut.test(), sut.fails, True, True)
        sut.prettyPrintTest(test)
        print(sut.failure())
        if config.fault:
            f = open((file_name + str(num) + ".test"),"w")
            f.writelines(str(sut.failure())) 
            f.writelines('\nReduced test now has ' + str(len(test)) + ' steps')
            f.close()
   
    return ok
 
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('timeout', type=int, default=60)
    parser.add_argument('seed', type=int, default=None)
    parser.add_argument('depth', type=int, default=100)
    parser.add_argument('width', type=int, default=100)
    parser.add_argument('fault', type=int, default=0)
    parser.add_argument('coverage', type=int, default=0)
    parser.add_argument('running', type=int, default=0)
    parsed_args = parser.parse_args(sys.argv[1:])
    return (parsed_args, parser)

def main():
    global start,config,sut,R,nonerror,error,file_name,num,actioncount
    num = 0
    actioncount = 0
    file_name = 'failurefile'
    parsed_args, parser = parse_args()
    config = make_config(parsed_args, parser)
    print('Random testing={}'.format(config))
    sut = SUT.sut()
    R = random.Random(config.seed)
    start = time.time()
    elapsed = time.time() - start
    states = [sut.state()]
    nonerror = []
    error = []
    news = None
    i = 0
    
    while(time.time() < start + config.timeout):
        for s in states:
	    i += 1
	    if (time.time() > start + config.timeout):
                break
            sut.restart()

            sut.backtrack(s)

            for w in xrange(0, config.width):

                for d in xrange(0, config.depth):
		    if (time.time() > start + config.timeout):
                        break 

                    ok = check_action()

		    news = sut.newStatements()

                    if not ok:
			error.append(sut.currStatements())

                        break

                    if((len(news)>0) and (not ((news in error) or (news in nonerror)))):

                        states.insert(i-1,sut.state())

                        nonerror.append(sut.currStatements())

		if (config.fault):
			    f = open("failure_file" + str(failureCount) + ".test", "w")
			    j = 0
		       	    for (s_reduces, _, _) in S:
				    steps_reduce = "# STEP " + str(j)
				    print >> f, sut.prettyName(s_reduces).ljust(80 - len(steps_reduce), ' '), steps_reduce
				    j += 1
			    f.close()

                             
    if config.coverage:

        sut.internalReport()

    
    print "Running time: ", time.time() - start
    print "Bugs Found: ",num
    print "No. of actions: ", actioncount
    
    



if __name__ == '__main__':
    main()
