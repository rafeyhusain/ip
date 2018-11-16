#!/usr/bin/env bash

DATE=$(date +"%Y%m%d%H%M")
TEMP=`mktemp -d`
PBI_OUTPUT=/srv/ftp/pbi-content
CATALOG_DIR=$(ls /srv/ftp/catalog -t|head -1)
CATALOG_DIR_PATH=/srv/ftp/catalog/$CATALOG_DIR
mkdir $PBI_OUTPUT/$DATE


for CC in id hk my ph sg th vn
do
    cut -d , -f9 $CATALOG_DIR_PATH/discovery-$CC.csv | sort -u >$TEMP/keyword_$CC.txt
    cut -d , -f3 $CATALOG_DIR_PATH/price-comparison-$CC.csv| sort -u >>$TEMP/keyword_$CC.txt
    cut -d , -f3 $CATALOG_DIR_PATH/coupon-$CC.csv | sort -u >>$TEMP/keyword_$CC.txt

    python ../keyword-planner/keyword-planner.py $CC --stats $TEMP/keyword_$CC.txt>$PBI_OUTPUT/$DATE/keyword-$CC.csv 2>>$PBI_OUTPUT/$DATE/error.log

    head -q -n1 $PBI_OUTPUT/$DATE/keyword-$CC.csv > $PBI_OUTPUT/$DATE/keyword.csv
done

tail -q -n+2 $PBI_OUTPUT/$DATE/keyword-*.csv >> $PBI_OUTPUT/$DATE/keyword.csv
