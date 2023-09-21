# CS-6120-23-Task-5
This repo contains the code for the 5th task of the course. The entirety of the code is in the file `my_dominance_code_with_tests.py`.
I have implemented dominators, the dominator tree, and the dominance frontier.
I have also implemented tests for the first two.
The test for the 1st one first removes backedges from the CFG, then for each block recursively computes the paths from the entry block to it.
It then checks to see whether the computed dominators for the block are present in all of the paths.
For the 2nd one, the test checks to see whether the parent-child relation of the tree follows the dominance relation.
I did not implement a test for the dominance frontier because I felt that the test itself is as complicated as the implementation, and it does not have any
added value in terms of correctness.
I therefore stopped at manual inspection.

Currently, there are two active `print` statements in the python file, which correspond to the outputs of the two tests.
Both of these should print `True`.
I have included the script `experiment.sh`, which goes through the programs in the `core` folder in the canonical Bril benchmarks, feeds them to the
python fle, and prints the outputs in the file `res.txt`.
One can then inspect this file to see if there exist some `False` outcomes.
You can uncomment various `print` statements to see different outputs, e.g., dominators and dominance frontier.
