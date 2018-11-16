#!/bin/sh

DATE=$(date +"%Y%m%d%H%M")
OUTPUT=/srv/ftp/workable

mkdir -p $OUTPUT/$DATE

python2.7 workable.py > $OUTPUT/$DATE/candidates.csv 2>> $OUTPUT/$DATE/error.log
