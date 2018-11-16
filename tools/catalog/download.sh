#!/bin/sh

DATE=$(date +"%Y%m%d%H%M")
OUTPUT=/srv/ftp/catalog

mkdir -p $OUTPUT/$DATE

for CC in id hk my ph sg th vn
do
    python2.7 discovery.py $CC > $OUTPUT/$DATE/discovery-$CC.csv 2>> $OUTPUT/$DATE/error.log
    python2.7 price-comparison.py $CC > $OUTPUT/$DATE/price-comparison-$CC.csv 2>> $OUTPUT/$DATE/error.log
    python2.7 coupon.py $CC > $OUTPUT/$DATE/coupon-$CC.csv 2>> $OUTPUT/$DATE/error.log
    python2.7 stores.py $CC > $OUTPUT/$DATE/stores-$CC.csv 2>> $OUTPUT/$DATE/error.log
    python2.7 comparables.py $CC > $OUTPUT/$DATE/comparables-$CC.csv 2>> $OUTPUT/$DATE/error.log

    head -q -n1 $OUTPUT/$DATE/coupon-$CC.csv >$OUTPUT/$DATE/coupon.csv 2>> $OUTPUT/$DATE/error.log
    head -q -n1 $OUTPUT/$DATE/discovery-$CC.csv > $OUTPUT/$DATE/discovery.csv
    head -q -n1 $OUTPUT/$DATE/price-comparison-$CC.csv > $OUTPUT/$DATE/price-comparison.csv
    head -q -n1 $OUTPUT/$DATE/stores-$CC.csv > $OUTPUT/$DATE/stores.csv
    head -q -n1 $OUTPUT/$DATE/comparables-$CC.csv > $OUTPUT/$DATE/comparables.csv
done

tail -q -n+2 $OUTPUT/$DATE/coupon-*.csv >>$OUTPUT/$DATE/coupon.csv
tail -q -n+2 $OUTPUT/$DATE/discovery-*.csv >> $OUTPUT/$DATE/discovery.csv
tail -q -n+2 $OUTPUT/$DATE/price-comparison-*.csv >> $OUTPUT/$DATE/price-comparison.csv
tail -q -n+2 $OUTPUT/$DATE/stores-*.csv >> $OUTPUT/$DATE/stores.csv
tail -q -n+2 $OUTPUT/$DATE/comparables-*.csv >> $OUTPUT/$DATE/comparables.csv
