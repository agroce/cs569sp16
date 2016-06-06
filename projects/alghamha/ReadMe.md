

## CS 569 Project - Alghamha ##
### Test Generator Algorithms Usage Instructions ###


#### Introduction ####

Generating test cases for a Software Under Test (SUT) is not an easy task as there are many approaches and techniques that can be adopted depending on the SUT and the main objective behind its testing. Moreover, it is more challenging to generalize the test generator on deferent SUTs. The most easiest and effective approach is Random Testing as it is simple to implement, fast to explore SUTs, efficient when executing  actions and provide great capabilities in finding faults. Therefore, in this project there are two algorithms have been implemented. The first algorithm’s called “PROP” that combines both sequential and random tester techniques based on randomly selected probability to replay back good test cases those are saved whenever new branches get discovered. The aim of this algorithm is searching for faults as quickly as possible by taking advantage of simple random generator speed. The second algorithm’s called “Grouping” that uses the same idea of selecting random probabilities the saved good test cases to be replayed back but instead of using the sequential algorithm we make the algorithm focus on randomly selected group of actions for some time. These algorithms can be used through an easy interface that will be described in “How to Use the Test Generator Algorithm” section.

#### How to Use The Test Generator Algorithm ####

The software can be used in TSTL under generator folder as follows:

` python mytester.py -t 3 -s 2 -d 100 -l 100 -f True -c True -r True -a prop -p True -P 0.5`

#### Description of Each Parameter ####

Here are a description of each parameter along with its default value:

```bash
  -h, --help            show this help message and exit
  -t [TIMEOUT], --timeout [TIMEOUT]
                        Timeout will be parsed in seconds - The default value
                        is 60 seconds
  -s [SEEDS], --seeds [SEEDS]
                        The number of seeds required. The default value is 0
  -d [DEPTH], --depth [DEPTH]
                        The depth of each test case. The default is 100
  -l [LENGTH], --length [LENGTH]
                        The length/Memory. The default value is 100
  -f [{True,False}], --FaultsEnabled [{True,False}]
                        Save Test Case when Failure is discovered. The default
                        value is True
  -c [{True,False}], --CoverageEnabled [{True,False}]
                        Report Code coverage. The default value is True
  -r [{True,False}], --RunningEnabled [{True,False}]
                        Check Coverage on the fly while running. The default
                        value is True
  -a [{prop,grouping}], --algorithm [{prop,grouping}]
                        There are 2 Algorithms implemented here. The first is
                        called [prop] that uses Random selections based on
                        sepcified propability. The second Algorithm is called
                        [grouping] that selects a group of actions and
                        concentrate on this group using automatically assigned
                        depths based on the length of enabled actions. The
                        default algorithm is [prop]
  -p [{True,False}], --propertyCheck [{True,False}]
                        Check All properties defined in the SUT. The default
                        Value is False
  -P [PROP], --Prop [PROP]
                        Assign the propability that can be used for both
                        algorithms. The default value is 0.5

```


### References ###
 

1- [TSTL: the Template Scripting Testing Language]
[TSTL: the Template Scripting Testing Language]: https://github.com/agroce/tstl
2- [cs569sp16 Repo]
[CS569sp16 Repository]: https://github.com/agroce/cs569sp16/blob/master/readings.txt
