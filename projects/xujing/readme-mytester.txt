In this test script, I add a new option with quicktest method we learn from lecture. With the method, the code will generate new test cases for future test. If we want to use this option, just set 1 at end of the command. Here is the example:
> python2.7 mytester.py 30 1750 100 10 1 1 1 1 
The command means, timeout = 30, seed = 1750,  deepth = 100, width = 10, open show faults, show coverage, running, and quicktest generate option.
Then we will get a file called quicktest.0, in there we can found test cases.
If we do not need to generate the quicktest cases, then we can just set 0 instead of 1 in the command:
>python2.7 mytester.py 30 1750 100 10 1 1 1 0
