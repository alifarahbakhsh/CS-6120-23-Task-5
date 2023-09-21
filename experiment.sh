#!/bin/bash
> res.txt
for FILE in ../../bril-repo/bril/benchmarks/core/*.bril; do echo $FILE; OUT=$(bril2json < $FILE | python my_dominance_code_with_tests.py); echo -e "$FILE\n$OUT" | tee -a res.txt; done