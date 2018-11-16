#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse, codecs, datetime, pandas, sys, os, time, urlparse

reload(sys)
sys.setdefaultencoding("UTF-8")

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('feed', type=argparse.FileType('r'), help=(''))


def main(argv):
    args = argparser.parse_args()

    csv = pandas.read_csv(args.feed, error_bad_lines=False)

    lps = {}

    for index, line in csv.iterrows():
        try:
            tracking_url = line[14]
            query = urlparse.urlparse(tracking_url).query
            url = urlparse.parse_qs(query)['url'][0]
            path = urlparse.urlparse(url).path
            unique = "-".join(path.split("-")[0:-1])

            if unique not in lps:
                lps[unique] = []
            lps[unique].append(tracking_url)

        except Exception, e:
            pass

    for key, value in lps.iteritems():
        if len(value) > 1:
            print value[0]


if __name__ == '__main__':
    main(sys.argv)
