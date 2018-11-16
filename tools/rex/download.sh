#!/bin/sh

DB=http://es-master.ipricegroup.com:9200
DATE=$(date +"%Y%m%d%H%M")

OUTPUT=/srv/ftp/rex

mkdir -p $OUTPUT/$DATE
rm -f input/*.json

elasticdump --input=$DB/rules --output=input/rex.json --type=data --limit=1000 --timeout=3000000 \
            --searchBody '{"query":{"match_all":{}}}' \
            2>&1 >> $OUTPUT/$DATE/error.log

python2.7 rex.py input/rex.json > $OUTPUT/$DATE/rex.csv 2>> $OUTPUT/$DATE/error.log

