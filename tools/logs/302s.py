#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse, codecs, datetime, pandas, sys, os, time, urllib

reload(sys)
sys.setdefaultencoding("UTF-8")

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('cc', type=str, help=('Country code).'))
argparser.add_argument('log', type=argparse.FileType('r'), help=(''))
argparser.add_argument('redirects', type=argparse.FileType('r'), help=(''))
argparser.add_argument('mode', choices=['cleanup', 'create'], help=(''))


def parse_landing_pages(cc, reader):
    landing_pages = {}

    if cc in ['hk', 'my', 'ph', 'sg']:
        filters = ['/black/', '/gold/', '/blue/', '/brown/', '/white/', '/pink/', '/red/', '/green/', '/silver/',
                   '/purple/', '/orange/', '/yellow/', '/grey/', '/beige/', '/multicolour/']
    elif cc == 'th':
        filters = ['/สดำ/', '/สทอง/', '/สนำเงน/', '/สนำตาล/', '/สขาว/', '/สชมพ/', '/สแดง/', '/สเขยว/', '/สเงน/',
                   '/สมวง/', '/สสม/', '/สเหลอง/', '/สเทา/', '/สเบจ/', '/หลากสสน/']
    elif cc == 'vn':
        filters = ['/den/', '/vang-gold/', '/xanh-duong/', '/nau/', '/trang/', '/hong/', '/do/', '/xanh-la/', '/bac/',
                   '/tim/', '/cam/', '/vang/', '/xam/', '/be/', '/nhieu-mau/']
    elif cc == 'id':
        filters = ['/hitam/', '/gold/', '/biru/', '/cokelat/', '/putih/', '/pink/', '/merah/', '/hijau/', '/silver/',
                   '/ungu/', '/oren/', '/kuning/', '/abu-abu/', '/beige/', '/multicolour/']

    filters += ['mailto', 'http', '.php', '.asp', '/coupons/', '/compare/', '/harga/', '/gia-ban/', '/ราคา/']

    csv = pandas.read_csv(reader)

    for index, line in csv.iterrows():
        if pandas.notnull(line['URL']):
            add = True
            url = urllib.unquote(line['URL']).lower()
            for filter in filters:
                if filter in url:
                    add = False
                    break
            if add == True:
                if not url in landing_pages:
                    landing_pages[url] = 0
                landing_pages[url] = landing_pages[url] + 1

    return [k for k, v in landing_pages.iteritems() if v > 1]


def parse_redirects(cc, reader):
    if cc in ['hk', 'my', 'ph', 'sg']:
        gender = ['men', 'women']
    elif cc == 'th':
        gender = ['ผชาย', 'ผหญง']
    elif cc == 'vn':
        gender = ['nam', 'nu']
    elif cc == 'id':
        gender = ['wanita', 'pria']

    redirects = []

    for line in reader:
        columns = line.split(",")

        src = columns[0].lower()
        dest = columns[1].strip("\n").lower()

        redirects.append([src, dest])

        # add gender pages
        if src.count("/") > 2:
            srcp = src.split("/")
            destp = dest.split("/")
            for g in gender:
                redirects.append(["/".join(srcp[0:2] + [g] + srcp[2:]), "/".join(destp[0:2] + [g] + destp[2:])])
                continue

    return redirects


def parse_rewrites(cc, reader):
    rewrites = []

    for line in reader:
        columns = line.split(" ")
        rewrites.append([columns[1][1:-1].lower(), columns[2].lower()])

    return rewrites


def main(argv):
    args = argparser.parse_args()

    # load input
    landing_pages = parse_landing_pages(args.cc.lower(), args.log)

    if args.mode == "create":
        redirects = parse_redirects(args.cc.lower(), args.redirects)

    elif args.mode == "cleanup":
        redirects = parse_rewrites(args.cc.lower(), args.redirects)

    redirects.sort(key=lambda s: len(s[0]), reverse=True)

    # calculate
    rewrites = []
    for lp in landing_pages:
        for redirect in redirects:
            if redirect[0] in lp:
                rewrites.append([lp, lp.replace(redirect[0], redirect[1])])
                break

    # print
    rewrites.sort()
    for rewrite in rewrites:
        # rewrite ^/20th-century-fox/electronics/$ /20th-century-fox/ permanent;
        sys.stderr.write("rewrite ^%s$ %s permanent;\n" % (rewrite[0], rewrite[1]))
        print "rewrite ^%s$ %s permanent;" % (rewrite[0], rewrite[1])


if __name__ == '__main__':
    main(sys.argv)
