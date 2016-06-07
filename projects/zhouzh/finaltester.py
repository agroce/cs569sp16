import os
import sys

current_working_dir = os.getcwd()
sys.path.append(current_working_dir)


from collections import namedtuple
import sut as SUT
import random
import time
import traceback
import argparse

sut  = SUT.sut()
nbugs = 0

def parse_args():
     parser = argparse.ArgumentParser()

     parser.add_argument('timeout', type=int, default=60, help='Timeout in seconds. (60 default)')
     parser.add_argument('seed', type=int, default=None, help='Random seed. (default = None)')
     parser.add_argument('depth', type=int, default=100, help='Maximum search depth. (100 default)')
     parser.add_argument('width', type=int, default=10000, help='Maximum memory. (10000 default)')
     parser.add_argument('faults', type=int, default=0, choices=[0, 1], help='Check for faults or not. 1 for check, 0 for do not check (0 default)')
     parser.add_argument('coverage', type=int, default=0, choices=[0, 1] ,help='report coverage or not. 1 for report, 0 for do not report(0 default)')
     parser.add_argument('running', type=int, default=0, choices=[0, 1], help='Produce running branch coverage report.')
     parsed_args = parser.parse_args(sys.argv[1:])

     return (parsed_args, parser)


def make_config(pargs, parser):

     pdict = pargs.__dict__
     key_list = pdict.keys()
     arg_list = [pdict[k] for k in key_list]
     Config = namedtuple('Config', key_list)
     nt_config = Config(*arg_list)
     return nt_config


def saveFaults(sut, Config, faults_file):
    global nbugs
    print "Found A Bug! number of bugs:", nbugs
    print sut.failure()
    print "Reducing......"

    reduction = sut.reduce(sut.test(), sut.fails, True, True)

    sut.prettyPrintTest(reduction)
    print sut.failure()

    if Config.faults == 1:
        sut.saveTest(reduction, faults_file + str(nbugs) + ".test")


def mutate(test, r, Config, faults_file):
    global nbugs
    tcopy = list(test)
    i = r.randint(0,len(tcopy))
    sut.replay(tcopy[:i])
    e = sut.randomEnabled(r)
    isGood = sut.safely(e)
    if not isGood:
        nbugs += 1
        saveFaults(sut, Config, faults_file)
        sut.restart()
    else:
        trest = [e]
        for s in tcopy[i+1:]:
            if s[1]():
                trest.append(s)
                isGood = sut.safely(s)
                if not isGood:
                    nbugs += 1
                    saveFaults(sut, Config, faults_file)
                    sut.restart()
                tcopy = test[:i]+trest
    return tcopy


def crossover(test, test2, r, Config, faults_file):
    global nbugs
    tcopy = list(test)
    i = r.randint(0,len(tcopy))
    sut.replay(tcopy[:i])
    trest = []
    for s in test2[i:]:
        if s[1]():
            trest.append(s)
            isGood = sut.safely(s)
            if not isGood:
                nbugs += 1
                saveFaults(sut, Config, faults_file)
                sut.restart()
    tcopy = test[:i]+trest

    return tcopy



def main():
    global nbugs
    parsed_args, parser = parse_args()
    Config = make_config(parsed_args, parser)

    print ('testing using config={}'.format(Config))

    sut.silenceCoverage()
    sut.restart()

    R = random.Random()
    R.seed(Config.seed)

    start = time.time()

    ntests = 0

    faults_file = "failure"

    population = []

    population_time = Config.timeout / 3

    while time.time() - start < population_time:

        ntests += 1
        sut.restart()
        for d in xrange(0, Config.depth):
            act = sut.randomEnabled(R)

            isGood = sut.safely(act)
            elapsed = time.time() - start
            population.append((list(sut.test()), set(sut.currStatements())))

            if Config.running:
                if sut.newBranches() != set([]):
                    print "ACTION:", act[0]
                    for b in sut.newBranches():
                        print time.time()-start, len(sut.allBranches()), "New branch", b
                if sut.newStatements() != set([]):
                    print "ACTION:", act[0]
                    for s in sut.newStatements():
                        print time.time()-start, len(sut.allStatements()),"New statement",s

            if not isGood:
                nbugs += 1
                saveFaults(sut, Config, faults_file)
                sut.restart()

            if elapsed >= Config.timeout / 3:
                print "Stopping Test Due To Timeout, Terminated at Length", len(sut.test())
                print time.time()-start, "TOTAL RUNTIME"
                print ntests, "EXECUTED"
                break

    mutate_start = time.time()
    while time.time() - mutate_start < Config.timeout - population_time:
        sortPop = sorted(population,key = lambda x: len(x[1]),reverse=True)
        (t,s) = R.choice(population)
        (t2,s) = R.choice(population)
        c = crossover(t, t2, R, Config, faults_file)
        m = mutate(t, R, Config, faults_file)
        elapsed = time.time() - mutate_start
        population.append((m, sut.currStatements()))
        population.append((c, sut.currStatements()))


        if elapsed >= Config.timeout / 3:
            print "Stopping Test Due To Timeout, Terminated at Length", len(sut.test())
            print time.time()-start, "TOTAL RUNTIME"
            print ntests, "EXECUTED"
            break


    if Config.coverage == 1:
        sut.internalReport()

if __name__ == '__main__':
    main()
