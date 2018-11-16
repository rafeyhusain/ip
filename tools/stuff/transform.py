#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse, pandas, json, re, sys, urlparse

reload(sys)
sys.setdefaultencoding("UTF-8")

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('file', type=str, help=('File with one keyword per line).'))


def main(argv):
    args = argparser.parse_args()
    csv = pandas.read_csv(args.file, error_bad_lines=False)

    print '"%s","%s","%s","%s","%s"' % ("keyword", "position", "url", "domain", "title")

    for index, line in csv.iterrows():
        for i in xrange(1, 10):

            try:
                url = urlparse.urlparse(line['#%02d URL' % i]).netloc
            except Exception:
                url = ""

            print '"%s","%s","%s","%s","%s"' % (line['Input'], i, line['#%02d URL' % i], url, line['#%02d Title' % i])


if __name__ == '__main__':
    main(sys.argv)
