import sut as SUT
import sys
import random
import time
import argparse
from collections import namedtuple

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('timeout', type=int, default=60, help='Time in seconds for testing.')
    parser.add_argument('seed', type=int, default=None, help='Seed for Python Random.')
    parser.add_argument('depth', type=int, default=100, help='Maximum length of a test generated.')
    parser.add_argument('width', type=int, default=100, help='Maximum memory/BFS queue/other parameter.')
    parser.add_argument('fault', type=int, default=0, help='Whether the tester checks for faults in the SUT.')
    parser.add_argument('coverage', type=int, default=0, help='Whether a final coverage report produced.')
    parser.add_argument('running', type=int, default=0, help='Whether running info on branch coverage should be produced.')
    parsed_args = parser.parse_args(sys.argv[1:])
    return (parsed_args, parser)

def make_config(pargs, parser):
    pdict = pargs.__dict__
    key_list = pdict.keys()
    arg_list = [pdict[k] for k in key_list]
    Config = namedtuple('Config', key_list)
    nt_config = Config(*arg_list)
    return nt_config

def check_action():
    global num
    action = sut.randomEnabled(R)
    ok = sut.safely(action)
    elapsed = time.time() - start
    if config.running:
        if len(sut.newBranches()) > 0:
            print "ACTION:", action[0]
            for b in sut.newBranches():
                print elapsed, len(sut.allBranches()),"New branch",b
    
    if not ok:
        num += 1
        print "Found Bug" , num
        print "REDUCING..."
        startReduce = time.time()
        test = sut.reduce(sut.test(), sut.fails, True, True)
        sut.prettyPrintTest(test)
        print(sut.failure())
        if config.fault:
            f = open((file_name + str(num) + ".test"),"w")
            f.writelines(str(sut.failure())) 
            f.writelines('\nReduced test has ' + str(len(test)) + ' steps')
            f.close()
        error.append(sut.currStatements())
    return ok 

def main():
    global start,config,sut,R,nonerror,error,file_name,num
    num = 0
    file_name = 'failurefile'
    parsed_args, parser = parse_args()
    config = make_config(parsed_args, parser)
    print('Random testing using config={}'.format(config))
    sut = SUT.sut()
    R = random.Random(config.seed)
    start = time.time()
    elapsed = time.time() - start
    states = [sut.state()]
    nonerror = []
    error = []
    news = None
    
    while(time.time() < start + config.timeout):
        for s in states:
            sut.restart()
            sut.backtrack(s)
            for w in xrange(0, config.width):
                for d in xrange(0, config.depth):
                    ok = check_action()
		    news = sut.newStatements()
                    if not ok:
                        break
                    if((len(news)>0) and (not ((news in error) or (news in nonerror)))):
                        states.insert(0,sut.state())
                        nonerror.append(sut.currStatements())
                             
    if config.coverage:
        sut.internalReport()

    print "Bugs ",num


if __name__ == '__main__':
    main()
