#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse, codecs, datetime, pandas, sys, os, time, urllib

reload(sys)
sys.setdefaultencoding("UTF-8")

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('input', type=argparse.FileType('r'), help=(''))


def main(argv):
    args = argparser.parse_args()

    # open file
    csv = pandas.read_csv(args.input)

    # group them by landing page by week/month
    csv = csv.groupby(['ipg:week', 'ipg:exitUrl']).count()
    print csv

    # remove parameters from exitUrl

    # compare groups in how much they differ

    # output

    pass


if __name__ == '__main__':
    main(sys.argv)
