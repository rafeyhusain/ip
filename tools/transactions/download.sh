#!/bin/bash

# init xvfb
/etc/init.d/xvfb start
export DISPLAY=:1

# create the output folder
DATE=$(date +"%Y%m%d%H%M")
OUTPUT=/srv/ftp/transactions
mkdir -p $OUTPUT/$DATE

# get the last 6 months
LAST_6_MONTHS=()

for ((i=0;i<6;i++)); do
    LAST_6_MONTHS[$i]=$(date "+%Y-%m" -d "$i month ago")
done

# get the data for each month and add it to the yearly file
for i in ${LAST_6_MONTHS[@]}
do
    # sync
    python sync.py $i all --testing False --dry_run False > $OUTPUT/$DATE/sync-$i.csv 2>> $OUTPUT/$DATE/sync-errors.log
    if [ ! -f $OUTPUT/$DATE/sync-${i%%-*}.csv ]; then
        head -n1 $OUTPUT/$DATE/sync-$i.csv > $OUTPUT/$DATE/sync-${i%%-*}.csv
    fi
    if [ ! -f $OUTPUT/$DATE/sync.csv ]; then
        head -n1 $OUTPUT/$DATE/sync-$i.csv > $OUTPUT/$DATE/sync.csv
    fi
    tail -n+2 $OUTPUT/$DATE/sync-$i.csv | tee -a $OUTPUT/$DATE/sync-${i%%-*}.csv $OUTPUT/$DATE/sync.csv >/dev/null

    # transactions
    python download.py $i all transactions > $OUTPUT/$DATE/transactions-$i.csv 2>> $OUTPUT/$DATE/transactions-errors.log
    if [ ! -f $OUTPUT/$DATE/transactions-${i%%-*}.csv ]; then
        head -n1 $OUTPUT/$DATE/transactions-$i.csv > $OUTPUT/$DATE/transactions-${i%%-*}.csv
    fi
    if [ ! -f $OUTPUT/$DATE/transactions.csv ]; then
        head -n1 $OUTPUT/$DATE/transactions-$i.csv > $OUTPUT/$DATE/transactions.csv
    fi
    tail -n+2 $OUTPUT/$DATE/transactions-$i.csv | tee -a $OUTPUT/$DATE/transactions-${i%%-*}.csv $OUTPUT/$DATE/transactions.csv >/dev/null

    # performance
    python download.py $i all performance > $OUTPUT/$DATE/performance-$i.csv 2>> $OUTPUT/$DATE/performance-errors.log
    if [ ! -f $OUTPUT/$DATE/performance-${i%%-*}.csv ]; then
        head -n1 $OUTPUT/$DATE/performance-$i.csv > $OUTPUT/$DATE/performance-${i%%-*}.csv
    fi
    if [ ! -f $OUTPUT/$DATE/performance.csv ]; then
        head -n1 $OUTPUT/$DATE/performance-$i.csv > $OUTPUT/$DATE/performance.csv
    fi
    tail -n+2 $OUTPUT/$DATE/performance-$i.csv | tee -a $OUTPUT/$DATE/performance-${i%%-*}.csv $OUTPUT/$DATE/performance.csv >/dev/null
done

# cleanup all processes
ps -ef | grep firefox | grep marionette | awk '{print $2}' | xargs kill -9
ps -ef | grep geckodriver | awk '{print $2}' | xargs kill -9
