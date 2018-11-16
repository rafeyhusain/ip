#!/bin/bash

OUTPUT=output
LOG_DIR=201609211611

for cc in hk id my ph sg th vn
do
    python2.7 302s.py $cc $OUTPUT/$LOG_DIR/access-$cc.log input/redirect-$cc.csv create >> $OUTPUT/rewrite-$cc.conf.tmp
    python2.7 302s.py $cc $OUTPUT/$LOG_DIR/access-$cc.log input/rewrite-$cc.conf cleanup >> $OUTPUT/rewrite-$cc.conf.tmp
    sort -u $OUTPUT/rewrite-$cc.conf.tmp > $OUTPUT/rewrite-$cc.conf
    rm -f $OUTPUT/rewrite-$cc.conf.tmp
done
