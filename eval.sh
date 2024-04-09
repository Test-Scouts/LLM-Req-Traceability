#!/usr/bin/bash

# Runs src/eval.py and logs the logs to res
# Also concatinates all the evaluation results into a single file

now=$(date +"%F/%H:%M:%S.%N")
mkdir "res" &> /dev/null;
mkdir "res/$(date +"%F")" &> /dev/null;
mkdir "res/$now" &> /dev/null;
logfile="./res/${now}/eval.log"
outfile="./res/${now}/res.log"

python src/eval.py &> ${logfile}

for m in ./out/*; do for d in ${m}/*; do for t in ${d}/*; do
    echo "${t}" >> "${outfile}";
    cat "${t}/eval.log" >> "${outfile}";
    echo "" >> "${outfile}";
done done done
