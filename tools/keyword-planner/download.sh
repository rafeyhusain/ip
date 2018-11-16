#!/bin/bash

DATE=$(date +"%Y%m%d%H%M")

OUTPUT=/srv/ftp/keyword-planner

mkdir -p $OUTPUT/$DATE

for cc in my id hk ph sg th vn
do

    for query in $(ls input/$cc/)
    do
        python keyword-planner.py --stats $cc input/$cc/$query > $OUTPUT/$DATE/$cc-${query%.*}.csv 2>> $OUTPUT/$DATE/error.log

        head -q -n1 $OUTPUT/$DATE/$cc-${query%.*}.csv > $OUTPUT/$DATE/$cc.csv
    done
    
    tail -q -n+2 $OUTPUT/$DATE/$cc-*.csv >> $OUTPUT/$DATE/$cc.csv

done


