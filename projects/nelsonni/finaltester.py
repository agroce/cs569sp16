import sut
import sys, time, math, random
from optparse import OptionParser
from itertools import compress
from operator import attrgetter, itemgetter
from deap import base
from deap import creator
from deap import tools

def init():
    global rgen, creator, toolbox
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Test", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()
    # Attribute generator
    toolbox.register("action", genActions, opts.depth)
    # Structure initializers
    toolbox.register("test", tools.initRepeat, creator.Test, toolbox.action, 1)
    toolbox.register("population", tools.initRepeat, list, toolbox.test)

    toolbox.register("evaluate", evalCoverage)
    toolbox.register("mate", crossover)
    toolbox.register("mutate", mutate)
    toolbox.register("select", selTournament, tournsize=10)

def main():
    global sut, rgen, nbugs, start, CXPB, MUTPB, NGEN
    sut = sut.sut()
    rgen = random.Random(opts.seed)
    CXPB, MUTPB, NGEN = 0.5, 0.2, 1
    best, timeclock = [], []
    nbugs, g, prev_best = 0, 0, 1

    init()
    start = time.time()

    while True:
        print("Building population")
        pop = toolbox.population(n=100)
        print("  n=%d" % len(pop))

        print("Start of evolution")

        fitnesses = list(map(toolbox.evaluate, pop))
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit

        while True:
            g += 1
            generation(g, pop)

            best_test = tools.selBest(pop, 1)[0]
            elapsed = time.time()-start
            if 0.02 > (best_test.fitness.values[0] - prev_best) / prev_best or elapsed > (0.95 * opts.timeout):
                break
            else:
                prev_best = max(best_test.fitness.values[0], prev_best)

        best_test = tools.selBest(pop, 1)[0]
        print("Best test has %s lines covered" % int(best_test.fitness.values[0]))
        best.append(best_test.fitness.values[0])

        elapsed = time.time()-start
        timeclock.append(elapsed) if not timeclock else timeclock.append(elapsed - timeclock[-1])
        average_time = sum(timeclock) / len(timeclock)
        print("elapsed: %f seconds out of %f seconds" % (elapsed, opts.timeout))

        if (elapsed + average_time) > opts.timeout:
            break

    overall_best = max(best)
    print("Overall best test has %s lines covered" % int(overall_best))

    if (opts.coverage):
        sut.internalReport()

def execute(statement):
    ok = sut.safely(statement)
    if not ok:
        if (opts.fault):
            captureFault()
        else:
            print "FAILURE LOCATED"
        sut.restart()
    if opts.plotting:
        capturePlotData()
    if opts.running:
        runtimeCoverage()

##
## methods related to Genetic Algorithm usage, as described by DEAP (https://github.com/deap/deap)
##

def generation(g, pop):
    print("-- Generation %i --" % g)
    offspring = toolbox.select(pop, len(pop))
    offspring = list(offspring)

    for child1, child2 in zip(offspring[::2], offspring[1::2]):
        if random.random() < CXPB:
            toolbox.mate(child1[0][0], child2[0][0])
            del child1.fitness.values
            del child2.fitness.values

    for mutant in offspring:
        if random.random() < MUTPB:
            toolbox.mutate(mutant[0][0])
            del mutant.fitness.values

    invalid_tests = [test for test in offspring if not test.fitness.valid]
    fitnesses = map(toolbox.evaluate, invalid_tests)
    for test, fit in zip(invalid_tests, fitnesses):
        test.fitness.values = fit

    print("  Evaluated %i tests" % len(invalid_tests))

    pop[:] = offspring

    fits = [test.fitness.values[0] for test in pop]

    length = len(pop)
    mean = sum(fits) / length
    sum2 = sum(x*x for x in fits)
    std = abs(sum2 / length - mean**2)**0.5

    print("  Min %s lines" % min(fits))
    print("  Max %s lines" % max(fits))
    print("  Avg %s lines" % mean)
    print("  Std %s lines" % std)

    print("-- End of (successful) evolution --")

def genActions(limit):
    sut.restart()
    for s in xrange(0,limit):
        r = sut.randomEnabled(rgen)
        execute(r)
    return (list(sut.test()),set(sut.currBranches()))

def evalCoverage(individual):
    sut.replay(individual[0][0])
    return len(sut.currBranches()),

def selTournament(tests, k, tournsize):
    chosen = []
    for i in xrange(k):
        aspirants = [random.choice(tests) for i in xrange(k)]
        chosen.append(max(aspirants, key=attrgetter("fitness")))
    return chosen

def mutate(test):
    tcopy = list(test)
    i = rgen.randint(0,len(tcopy))
    sut.replay(tcopy[:i])
    e = sut.randomEnabled(rgen)
    execute(e)
    trest = [e]
    for s in tcopy[i+1:]:
        if s[1]():
            trest.append(s)
            execute(s)
    tcopy = test[:i]+trest
    if len(sut.newCurrBranches()) != 0:
        print "NEW BRANCHES DUE TO MUTATION:",sut.newCurrBranches()
    return tcopy,

def crossover(test1, test2): 
    tcopy = list(test1)
    i = rgen.randint(0,len(tcopy))
    sut.replay(tcopy[:i])
    trest = []
    for s in test2[i:]:
        if s[1]():
            trest.append(s)
            execute(s)
    tcopy = test1[:i]+trest
    if len(sut.newCurrBranches()) != 0:
        print "NEW BRANCHES DUE TO CROSSOVER:",sut.newCurrBranches()
    return tcopy, test2

##
## methods related to project requirements; i.e. runtime coverage and fault capture/output
##

def captureFault():
    'Print failure state and reduction, save to file'
    nbugs += 1
    print "FAILURE LOCATED:"
    print sut.failure()
    print "REDUCING FAILURE:"
    R = sut.reduce(sut.test(),sut.fails, True, True)
    sut.prettyPrintTest(R)
    print sut.failure()
    # output to file for each fault
    filename = 'failure%d.test' % nbugs
    sut.saveTest(R, filename)

def runtimeCoverage():
    'Handler for generating running info on branch and statement coverage'
    elapsed = time.time() - start

    if sut.newBranches() != set([]):
        for b in sut.newBranches():
            print elapsed, len(sut.allBranches()),"New branch", b

    if sut.newStatements() != set([]):
        for s in sut.newStatements():
            print elapsed, len(sut.newStatements()), "New statement", s

def parse_options(argv):
    global opts 
    parser = OptionParser()
    parser.add_option('-t', '--timeout', action="store", type="int", dest="timeout", default=30, 
        help="time in seconds for testing")
    parser.add_option('-s', '--seed', action="store", type="int", dest="seed", default=1, 
        help="seed used for random number generation")
    parser.add_option('-d', '--depth', action="store", type="int", dest="depth", default=100, 
        help="maximum length of a test")
    parser.add_option('-w', '--width', action="store", type="int", dest="width", default=1, 
        help="maximum width of a pool of tests")
    parser.add_option('-f', '--fault', action="store_true", dest="fault", default=False, 
        help="check for faults in the SUT")
    parser.add_option('-c', '--coverage', action="store_true", dest="coverage", default=True, 
        help="produce a final coverage report")
    parser.add_option('-r', '--running', action="store_true", dest="running", default=True, 
        help="produce running info on branch coverage")
    parser.add_option('-p', '--plotting', action="store_true", dest="plotting", default=False,
        help="produce time and coverage data for plotting")
    (opts, args) = parser.parse_args()

    if len(args) > 0:
        for idx,arg in enumerate(args):
            if idx == 0:
                opts.timeout = int(arg)
            elif idx == 1:
                opts.seed = int(arg)
            elif idx == 2:
                opts.depth = int(arg)
            elif idx == 3:
                opts.width = int(arg)
            elif idx == 4:
                opts.fault = bool(int(arg))
            elif idx == 5:
                opts.coverage = bool(int(arg))
            elif idx == 6:
                opts.running = bool(int(arg))
            elif idx == 7:
                opts.plotting = bool(int(arg))
            else:
                print "Error! Options out of bounds: too many parameters"
                sys.exit(1)

    if opts.timeout <= 0:
        print "Error! Option out of bounds: timeout (-t) option must be greater than 0 seconds."
        sys.exit(1)

if __name__ == "__main__":
    parse_options(sys.argv[1:])
    main()