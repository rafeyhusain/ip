#!/usr/bin/python

import codecs, operator, sys

file = codecs.open(sys.argv[1], "r", "utf-8")
wordcount = {}
for word in file.read().split():
    if word not in wordcount:
        wordcount[word] = 1
    else:
        wordcount[word] += 1
wordcount_sorted = sorted(wordcount.items(), key=operator.itemgetter(1))
for k in wordcount_sorted:
    print k[0], k[1]
