#!/bin/sh

DATE=$(date +"%Y%m%d%H%M")
OUTPUT=/srv/ftp/account-management/
LP=input/landing-pages.csv

mkdir -p $OUTPUT/$DATE

for CC in id hk my ph sg th vn
do
    python2.7 traffic-potential.py $CC $LP > $OUTPUT/$DATE/traffic-potential-$CC.csv 2>> $OUTPUT/$DATE/error.log
    head -q -n+2 $OUTPUT/$DATE/traffic-potential-$CC.csv > $OUTPUT/$DATE/traffic-potential.csv
done

tail -q -n+2 $OUTPUT/$DATE/traffic-potential-*.csv >> $OUTPUT/$DATE/traffic-potential.csv
