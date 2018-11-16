#!/bin/bash

DATE=$(date +"%Y%m%d%H%M")
OUTPUT=/srv/ftp/google-analytics

mkdir -p $OUTPUT/$DATE

CW=$(date +"%V")
CY=$(date +"%Y")

for query in $(ls input)
do
  for cc in MY ID HK PH SG TH VN
  do
    for i in $CW
    #for i in $(seq 1 $CW) 
    do
      python google-analytics.py $cc $CY-$i input/$query > $OUTPUT/$DATE/${query%.*}-$cc-$i.csv 2>> $OUTPUT/$DATE/errors.log

      head -q -n1 $OUTPUT/$DATE/${query%.*}-$cc-$i.csv > $OUTPUT/$DATE/${query%.*}-$cc.csv
    done

    tail -q -n+2 $OUTPUT/$DATE/${query%.*}-$cc-*.csv >> $OUTPUT/$DATE/${query%.*}-$cc.csv

    head -q -n1 $OUTPUT/$DATE/${query%.*}-$cc.csv > $OUTPUT/$DATE/${query%.*}.csv
  done

  tail -q -n+2 $OUTPUT/$DATE/${query%.*}-*-*.csv >> $OUTPUT/$DATE/${query%.*}.csv
done

# import csv to db
YESTERDAY=$(date -d "yesterday 13:00" '+%Y-%m-%d')
TABLES=('ga_acquisition' 'ga_conversions')
REPORTS=('bi-acquisition' 'bi-conversions')

for i in "${!TABLES[@]}"
do
  python ./../dataware-house/csv_importer/main.py \
        "ipg:date=='$YESTERDAY'" \
        "${TABLES[$i]}" \
        $OUTPUT/$DATE/"${REPORTS[$i]}".csv \
        $OUTPUT/$DATE/errors.log \
    2>> $OUTPUT/$DATE/errors.log
done
