import sut as SUT
from collections import namedtuple
import sys
import random
import time
import argparse





def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('timeout', type=int)
    parser.add_argument('seed', type=int)
    parser.add_argument('depth', type=int)
    parser.add_argument('width', type=int)
    parser.add_argument('fault', type=int,choices=[0,1])
    parser.add_argument('coverage', type=int,choices=[0,1])
    parser.add_argument('running', type=int, choices=[0,1])
    parsed_args = parser.parse_args(sys.argv[1:])
    return (parsed_args, parser)



def make_config(pargs, parser):
    pdict = pargs.__dict__
    key_list = pdict.keys()
    arg_list = [pdict[k] for k in key_list]
    Config = namedtuple('Config', key_list)
    nt_config = Config(*arg_list)
    return nt_config





def main():
    global start,config,sut,R,nonErrorSeq,ErrorSeq,fail_name,bug,act
    parsed_args, parser = parse_args()
    config = make_config(parsed_args, parser)
    fail_name = 'failurefile'
    nonErrorSeq = []
    ErrorSeq = []
    newSeq = None
    sut = SUT.sut()
    R = random.Random(config.seed)
    start = time.time()
    elapsed = time.time() - start
    states = [sut.state()]
    n = -1
    bug = 0
    act = 0

    while(time.time() < start + config.timeout):
        for s in states:
            
            if (time.time() > start + config.timeout):
                break
            n+=1
            sut.restart()
            sut.backtrack(s)
            for i in xrange(0, config.width):
                for j in xrange(0, config.depth):
                    if (time.time() > start + config.timeout):
                        break
                    action = sut.randomEnabled(R)
                    act+=1
                    ok = sut.safely(action)
                    elapsed = time.time() - start
   
                    if config.running:
                        if sut.newBranches() != set([]):                
                            for b in sut.newBranches():
                                print elapsed, len(sut.allBranches()),"New branch",b

                        if sut.newStatements() != set([]):
                            for s in sut.newStatements():
                                print elapsed, len(sut.allStatements()), "New statement", s

                    if elapsed > config.timeout:
                        print "Timeout: Stop testing."
                        break
   

                    if not ok:
                        bug += 1
                        print "Bug" , bug
                        startReduce = time.time()
                        r = sut.reduce(sut.test(), sut.fails, True, True)
                        sut.prettyPrintTest(r)
                        print(sut.failure())
                        if config.fault:
                            f = open((fail_name + str(bug) + ".test"),"w")
                            f.writelines(str(sut.failure())+ "\n") 
                            f.close()
                        ErrorSeq.append(sut.currStatements())

                    newSeq = sut.newStatements()

                    if not ok:
                        
                        break

                    if not (newSeq in nonErrorSeq):
                        if (len(newSeq)>0) :
                            states.insert(n,sut.state())
                            nonErrorSeq.append(sut.currStatements())
                        else:
                            continue
                    else:
                        states.insert(n,sut.state())
                        nonErrorSeq.append(sut.currStatements())                               
    if config.coverage:
        sut.internalReport()


    print "Total Bugs: ",bug
    print "Total actions: ", act
    print "Total Running time: ", time.time() - start

if __name__ == '__main__':

    main()
