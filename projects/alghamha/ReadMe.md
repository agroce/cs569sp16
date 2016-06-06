

## CS 569 Project - Alghamha ##
### Test Generator Algorithms Usage Instructions ###


#### Introduction ####



#### Using The Tester Algorithm Parameters ####

The software can be used in TSTL under generator folder as follows:

` python mytester.py -t 3 -s 2 -d 100 -l 100 -f True -c True -r True -a prop -p True -P 0.5`

#### Description of each parameter ####

Here are a description of each parameter along with its default value:

```bash
  -h, --help            show this help message and exit
  -t [T], -timeout [T]  Timeout will be parsed in seconds - The default value
                        is 60 seconds
  -s [S], -seeds [S]    The number of seeds required. The default value is 0
  -d [D], -depth [D]    The depth of each test case. The default is 100
  -l [L], -length [L]   The length/Memory. The default value is 100
  -f [F], -FaultsEnabled [F]
                        Save Test Case when Failure is discovered. The default
                        value is False
  -c [C], -CoverageEnabled [C]
                        Report Code coverage. The default value is False
  -r [R], -RunningEnabled [R]
                        Check Coverage on the fly while running. The default
                        value is False
  -a [A], -algorithm [A]
                        There are 2 Algorithms. [prop] is a Random algorithm
                        based on sepcified propability and [grouping] is
                        random algorithm concentrate on a group of actions for
                        automatically assigned depths based on the length of
                        enabled actions. The default algorithm is prop
  -p [P], -propertyCheck [P]
                        Check All properties defined in the SUT. The default
                        Value is False
  -P [P], -Prop [P]     Assign the propability that can used for both
                        algorithms. The default value is 0.5

```


### References ###
 

1- [TSTL: the Template Scripting Testing Language]
[TSTL: the Template Scripting Testing Language]: https://github.com/agroce/tstl
2- [cs569sp16 Repo]
[cs569sp16 Repo]: https://github.com/agroce/cs569sp16/blob/master/readings.txt
