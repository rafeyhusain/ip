#!/bin/bash

# write to directory with today's date
SAVEDATE=$(date +"%Y%m%d%H%M")
OUTPUT=/srv/ftp/scraper-logs/$SAVEDATE
mkdir -p $OUTPUT

# query logs from yesterday
QUERYDATE=$(date --date="1 day ago" +"%Y%m%d")
python scraper-logs.py --date=$QUERYDATE > $OUTPUT/scraper-log.csv 2> $OUTPUT/error.log
