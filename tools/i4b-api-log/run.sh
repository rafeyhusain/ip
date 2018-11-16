#!/usr/bin/env bash

DATE=$(date +"%Y-%m-%d")
OUTPUT=/srv/ftp/i4b-logs/$DATE
# check if /srv/ftp/logs existed
if [ ! -d "$OUTPUT" ]; then
    mkdir -p "$OUTPUT"
fi

# time in miliseconds
START_DATE_TIME=$(date --date="$DATE 00:00:00" +%s000)
END_DATE_TIME=$(date --date="$DATE 23:59:59" +%s000)

# aws configure
aws configure set aws_access_key_id AKIAIKJBTUWHSF6NDQRQ
aws configure set aws_secret_access_key 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
aws configure set default.region ap-southeast-1

# API-Gateway-Execution-Logs_jonia45lf2/production should not be hard code
aws logs filter-log-events --log-group-name \
    API-Gateway-Execution-Logs_jonia45lf2/production \
    --start-time $START_DATE_TIME \
    --end-time $END_DATE_TIME --output text > $OUTPUT/i4b.log 2>$OUTPUT/aws_logs_cmd_error.log
echo "finished download log from aws cloud watch"

# generate price-list endpoint log
awk -F' ' 'NF>1{$1=$2=$3=$4=""; a[$5] = a[$5]$0};END{for(i in a)print a[i]}' $OUTPUT/i4b.log | \
    awk '{$1=$1};1' | \
    grep "API Key ID: 05euz4r3s7" | \
    grep "price-list" > $OUTPUT/i4b.log.pricelist
# finished parse log file to csv file
cat $OUTPUT/i4b.log.pricelist | python ./parser.py > $OUTPUT/i4b-api-log-$DATE.csv 2>$OUTPUT/error.log
echo "finished parse log file to csv file"
