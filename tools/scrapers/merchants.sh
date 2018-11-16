#!/bin/bash

DATE=$(date +"%Y%m%d%H%M")
OUTPUT=/srv/ftp/scrapers

mkdir -p $OUTPUT/$DATE

for competitor in $(ls merchants)
do
    scrapy runspider merchants/${competitor%.*}.py -o $OUTPUT/$DATE/${competitor%.*}.csv 2>> $OUTPUT/$DATE/error.log & 
done

