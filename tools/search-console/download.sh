#!/bin/sh

DATE=$(date +"%Y%m%d%H%M")

OUTPUT=/srv/ftp/search-console

CW=$(date --date="4 days ago" +"%V")
CY=$(date --date="4 days ago" +"%Y")

mkdir -p $OUTPUT/$DATE

for cc in MY ID HK PH SG TH VN
do

  for i in $CW 
  do
    python search-console.py --pages 10000 $cc $CY-w$i > $OUTPUT/$DATE/10k-$cc-$i.csv 2>> $OUTPUT/$DATE/error.log

    head -q -n1 $OUTPUT/$DATE/10k-$cc-$i.csv > $OUTPUT/$DATE/10k-$cc.csv
  done
  tail -q -n+2 $OUTPUT/$DATE/10k-$cc-*.csv >> $OUTPUT/$DATE/10k-$cc.csv

  head -q -n1 $OUTPUT/$DATE/10k-$cc.csv > $OUTPUT/$DATE/10k.csv
done

tail -q -n+2 $OUTPUT/$DATE/10k-*-*.csv >> $OUTPUT/$DATE/10k.csv
