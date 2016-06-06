

## CS 569 Project - Alghamha ##
### Test Generator Algorithms Usage Instructions ###


#### Introduction ####

Generating test cases for a Software Under Test (SUT) is not an easy task as there are many approaches and techniques that can be adopted depending on the SUT and the main objective behind its testing. Moreover, it is more challenging to generalize the test generator on deferent SUTs. The most easiest and effective approach is Random Testing for its easy implementation, its efficiency in SUT exploration and its great results. Therefore, in this project these are two algorithms have been implemented. The first algorithm’s called “PROP” that combines both sequential and random tester techniques based on randomly selected probability to replay back good tests those are saved whenever new branches got discovered. The aim of this algorithm is searching for faults as quickly as possible by taking advantage of simple random generator speed. The second algorithm have the same idea of selecting random probabilities but instead of using the sequential algorithm we make the algorithm focus on randomly selected group of actions. These algorithms can be used through an easy interface that will be described in “How to Use The Test Generator Algorithm” section.

#### How to Use The Test Generator Algorithm ####

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
  -P [P], -Prop [P]     Assign the propability that can be used for both
                        algorithms. The default value is 0.5

```


### References ###
 

1- [TSTL: the Template Scripting Testing Language]
[TSTL: the Template Scripting Testing Language]: https://github.com/agroce/tstl
2- [cs569sp16 Repo]
[cs569sp16 Repo]: https://github.com/agroce/cs569sp16/blob/master/readings.txt
