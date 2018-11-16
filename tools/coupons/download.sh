#!/bin/sh

DB=http://es-master.ipricegroup.com:9200
DATE=$(date +"%Y%m%d%H%M")

OUTPUT=/srv/ftp/coupons

mkdir -p $OUTPUT/$DATE
rm -f input/*.json

for CC in id hk my ph sg th vn
do

	elasticdump --input=$DB/content_$CC/coupon --output=input/coupons-$CC.json --type=data --limit=1000 --timeout=3000000 \
	            --searchBody '{"query":{"match_all":{}},"_source":["name","created","expires","label","referral","referralMobile","store.url","category.url","popularity","type"]}' \
	            2>&1 >> $OUTPUT/$DATE/error.log

	python2.7 coupons.py input/coupons-$CC.json > $OUTPUT/$DATE/coupons-$CC.csv 2>> $OUTPUT/$DATE/error.log

	head -q -n1 $OUTPUT/$DATE/coupons-$CC.csv > $OUTPUT/$DATE/coupons.csv
done

tail -q -n+2 $OUTPUT/$DATE/coupons-*.csv >> $OUTPUT/$DATE/coupons.csv

