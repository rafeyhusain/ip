#!/bin/bash
# Requires credentials to be setup using 'aws configure'

DATE=$(date +"%Y%m%d%H%M")
OUTPUT=/srv/ftp/logs
TMP=`mktemp -d`

mkdir -p $OUTPUT/$DATE

aws s3 sync s3://iprice-prod-logs $TMP

for FILE in `ls $TMP/*.tar.gz`
do
	mkdir ${FILE%.*.*}
	tar -xz -C ${FILE%.*.*} -f $FILE
done

for FILE in `find $TMP -name "access*.gz"`
do
	gzip -d $FILE
done

for CC in HK ID MY PH SG TH VN
do

	echo '"Date","IP","URL","Parameters","HTTP Code","Size","User Agent"' >> $OUTPUT/$DATE/access-$CC-bots.csv
	echo '"Date","IP","URL","Parameters","HTTP Code","Size","User Agent"' >> $OUTPUT/$DATE/access-$CC-users.csv

	for FILE in `find $TMP -name "access*$CC*.log"`
	do
		cat $FILE | grep "bot" | sed -E 's/^\[(.+)\] - ([0-9.]+) - - "[A-Z]{3,7} ([^\?]+)(\?.*)? HTTP\/.\.." ([0-9]{3}) ([0-9])+ ([ 0-9\.\-]{5,25})?".*" "(.*)"/"\1","\2","\3","\4","\5\,"\6","\8"/' >> $OUTPUT/$DATE/access-$CC-bots.csv

		cat $FILE | grep -v "bot" | sed -E 's/^\[(.+)\] - ([0-9.]+) - - "[A-Z]{3,7} ([^\?]+)(\?.*)? HTTP\/.\.." ([0-9]{3}) ([0-9])+ ([ 0-9\.\-]{5,25})?".*" "(.*)"/"\1","\2","\3","\4","\5\,"\6","\8"/' >> $OUTPUT/$DATE/access-$CC-users.csv
	done
done

rm -fR $TMP
