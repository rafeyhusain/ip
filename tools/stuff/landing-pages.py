#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse, codecs, datetime, pandas, sys, os, time, urllib

reload(sys)
sys.setdefaultencoding("UTF-8")

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('file', type=argparse.FileType('r'), help=(''))


def main(argv):
    csv = pandas.read_csv(reader)


if __name__ == '__main__':
    main(sys.argv)
