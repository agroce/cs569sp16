import avlbug1 as avl
import random

DEPTH = 100
NUM_TESTS = 1000

for t in xrange(0,NUM_TESTS):
    print "STARTING TEST",t
    a = avl.AVLTree()
    for s in xrange(0,DEPTH):
        op = random.choice(["insert","delete","find"])
        val = random.randrange(1,20)
        print "STEP",s,op,val 
        if op == "insert":
            a.insert(val)
        if op == "delete":
            a.delete(val)
        if op == "find":
            a.find(val)
        assert(a.check_balanced())

