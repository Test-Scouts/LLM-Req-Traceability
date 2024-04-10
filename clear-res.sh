#!/usr/bin/bash

# Removes all the results from prior evaluations

for m in ./out/*; do for d in ${m}/*; do for t in ${d}/*; do
    rm "${t}/eval.log" &> /dev/null;
    rm "${t}/label-eval.log" &> /dev/null;
done done done
