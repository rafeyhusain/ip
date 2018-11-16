#!/bin/sh

DB=http://es-master.ipricegroup.com:9200
DATE=$(date +"%Y%m%d%H%M")

OUTPUT=/srv/ftp/content

mkdir -p $OUTPUT/$DATE
rm -f input/*.json

#for CC in hk
for CC in hk id my ph sg vn th
do

	elasticdump --input=$DB/content_$CC --output=input/$CC.json --type=data --limit=1000 --timeout=3000000 \
	            --searchBody '{"query":{"match_all":{}},"_source":["url","text","shortText","sideText","source.brand","source.category","source.gender","source.model","source.series","source.characteristic.c1","source.characteristic.c2","source.characteristic.c3", "title","meta","heading","image","internationalUrl.HK","internationalUrl.ID","internationalUrl.MY","internationalUrl.PH","internationalUrl.SG","internationalUrl.TH","internationalUrl.VN","specs","reviews","news","images.small","images.medium","images.large","updated","created","redirects","googleSearchVolume","crawlFrequency","addedSearchVolume","autoText"]}' \
	            2>&1 >> $OUTPUT/$DATE/error.log

	python2.7 content.py input/$CC.json > $OUTPUT/$DATE/content-$CC.csv 2>> $OUTPUT/$DATE/error.log
	python2.7 links.py input/$CC.json > $OUTPUT/$DATE/links-$CC.csv 2>> $OUTPUT/$DATE/error.log

	head -q -n1 $OUTPUT/$DATE/content-$CC.csv > $OUTPUT/$DATE/content.csv
	head -q -n1 $OUTPUT/$DATE/links-$CC.csv > $OUTPUT/$DATE/links.csv
done

tail -q -n+2 $OUTPUT/$DATE/content-*.csv >> $OUTPUT/$DATE/content.csv
tail -q -n+2 $OUTPUT/$DATE/links-*.csv >> $OUTPUT/$DATE/links.csv

