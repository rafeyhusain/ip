#!/bin/bash

DATE=$(date +"%Y%m%d%H%M")
OUTPUT=/srv/ftp/scrapers

mkdir -p $OUTPUT/$DATE

scrapy runspider products/chongiadung.py -o $OUTPUT/$DATE/chongiadung.csv 2> $OUTPUT/$DATE/error.log & 
scrapy runspider products/websosanh.py -o $OUTPUT/$DATE/websosanh.csv 2> $OUTPUT/$DATE/error.log &
scrapy runspider products/priceza.py -o $OUTPUT/$DATE/priceza.csv 2> $OUTPUT/$DATE/error.log &
scrapy runspider products/priceprice.py -o $OUTPUT/$DATE/priceprice.csv 2> $OUTPUT/$DATE/error.log &
