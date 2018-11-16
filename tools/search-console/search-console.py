#!/usr/bin/python

import argparse, datetime, urllib, socket, sys, re, random, time, simplejson

from datetime import date, timedelta
from googleapiclient import sample_tools
from progress.bar import Bar
from calendar import monthrange
from apiclient import errors

reload(sys)
sys.setdefaultencoding("UTF-8")
socket.setdefaulttimeout(10)

GA_IDS = {
    'SG': {
        'IPRICE': '75448761'
    },
    'MY': {
        'IPRICE': '75229758'
    },
    'ID': {
        'IPRICE': '75897118',
        'RAPPLER': '146691305'
    },
    'PH': {
        'IPRICE': '75445974',
        'RAPPLER': '146675449'
    },
    'TH': {
        'IPRICE': '79109064'
    },
    'VN': {
        'IPRICE': '75895336'
    },
    'HK': {
        'IPRICE': '75887160'
    }
}
GSC_IDS = {
    'SG': {
        'IPRICE': 'iprice.sg'
    },
    'MY': {
        'IPRICE': 'iprice.my'
    },
    'ID': {
        'IPRICE': 'iprice.co.id',
        'RAPPLER': 'kupon.rappler.com'
    },
    'PH': {
        'IPRICE': 'iprice.ph',
        'RAPPLER': 'coupons.rappler.com'
    },
    'TH': {
        'IPRICE': 'ipricethailand.com'
    },
    'VN': {
        'IPRICE': 'iprice.vn'
    },
    'HK': {
        'IPRICE': 'iprice.hk'
    }
}
PROTOCOL = {'IPRICE': 'https', 'SAYS': 'http', 'RAPPLER': 'http', 'JUICE': 'http'}
FILTERS = {'IPRICE': ['discovery-', 'coupon-', 'pc-'], 'SAYS': [' '], 'JUICE': [' '], 'RAPPLER': [' ']}
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('cc', type=str, help=('Country code).'))
argparser.add_argument('date', type=str, help=('Week-Month in ISO 8601 notation).'))
argparser.add_argument('--pages', type=int, help=('Top N pages).'))
argparser.add_argument('--file', type=str, help=('Transaction Files).'))

PAGE_SIZE = 5000


def get_top_landing_pages(service, cc, website, week, n):
    result = []
    query = {'ids': 'ga:' + GA_IDS[cc][website],
             'start_index': '1',
             'max_results': n,
             'start_date': get_date(week)[0],
             'end_date': get_date(week)[1],
             'sort': '-ga:sessions',
             'dimensions': 'ga:landingPagePath',
             'metrics': 'ga:sessions'}
    for cg in FILTERS[website]:
        query['filters'] = 'ga:medium==organic;ga:landingContentGroup1=@' + cg
        data = service.data().ga().get(**query).execute()
        result += [d + [cg.split('-')[0] if len(cg) > 0 else None] for d in data['rows']]
    return result


def get_keyword_data(service, cc, website, date, url, protocol, dimensions=''):
    uncatched_error = ''
    for n in range(0, 5):
        try:
            body = {
                'startDate': get_date(date)[0],
                'endDate': get_date(date)[1],
                'dimensions': dimensions,
                'dimensionFilterGroups': [{
                    'filters': [{
                        'dimension': 'page',
                        'expression': protocol + "://" + GSC_IDS[cc][website] + "/" + urllib.quote(url.encode('utf-8')),
                        'operator': 'equals'
                    }]
                }],
                'rowLimit': PAGE_SIZE
            }
            tmp = service.searchanalytics().query(
                siteUrl=protocol + "://" + GSC_IDS[cc][website] + "/",
                body=body).execute()
            if 'rows' in tmp:
                # when keyword and date are missed
                for item in tmp['rows']:
                    if not 'keys' in item:
                        item['keys'] = ['', '']

                return tmp['rows']
            # when there is no keyword and data
            else:
                return [{'keys': ['', ''], 'impressions': None, 'clicks': None, 'ctr': None, 'position': None}]
        except errors.HttpError, e:
            error = simplejson.loads(e.content)
            if (error['error'].get('code') == 403 or error['error'].get('code') == 429) and \
                    error['error'].get('errors')[0].get('reason') \
                    in ['rateLimitExceeded', 'userRateLimitExceeded', 'quotaExceeded']:
                uncatched_error = e
                # Apply exponential backoff.
                time.sleep((2 ** n) + random.randint(0, 1000) / 1000)
            else:
                print >> sys.stderr, 'Failed downloading: %s for %s (code: %s, reason: %s)' % (
                url, website, error['error'].get('code'), error['error'].get('errors')[0].get('reason'))
                return []
        except Exception, e:
            print >> sys.stderr, 'Failed downloading: %s (%s)' % (url, e.message)
            return []
    if uncatched_error != '':
        print >> sys.stderr, 'Failed downloading after 5 tries: %s (%s)' % (url, uncatched_error)
    return []


def get_date(date_str):
    parse_date = re.match('(\d{4})-([w|W])?(\d{2})', date_str)
    if parse_date:
        year = int(parse_date.group(1))
        if parse_date.group(2) is not None:
            week = parse_date.group(3)
            return get_date_by_week(year, week)
        else:
            month = parse_date.group(3)
            date_range = monthrange(int(year), int(month))
            return date(int(year), int(month), 1).isoformat(), \
                   date(int(year), int(month), date_range[1]).isoformat(), 'month', month
    else:
        print>> sys.stderr, "#Error: date format is not in yyyy-[W|w]dd."


def get_date_by_week(year, week):
    year = int(year)
    week = int(week)

    d = date(year, 1, 1)
    if (d.weekday() <= 3):
        d = d - timedelta(d.weekday())
    else:
        d = d + timedelta(7 - d.weekday())
    dlt = timedelta(days=(week - 1) * 7)
    return (d + dlt).isoformat(), (d + dlt + timedelta(days=6)).isoformat()


def initialize_service(argv, id):
    service, flags = sample_tools.init(
        argv, id, 'v3', __doc__, __file__, parents=[argparser],
        scope='https://www.googleapis.com/auth/' + id + '.readonly')
    return service


def output(cc, website, url, traffic, data, product):
    for row in data:
        if row['keys'][1] != "":
            print '"%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s"' % (
            cc, website, url, row['keys'][1], row['keys'][2], row['keys'][0].replace('"', '""'), row['impressions'],
            row['clicks'], row['ctr'], row['position'], traffic, product)


def get_urls(path):
    with open(path) as f:
        urls = f.readlines()
    return [[url.rstrip(), None, None] for url in list(set(urls))]


def main(argv):
    args = argparser.parse_args()

    print >> sys.stderr, '# Start: search-console data: %s, %s, %s, %s' % (
    args.cc, args.date, args.pages, datetime.datetime.now().time().isoformat())
    print u'\ufeff'.encode('utf8') + '"%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s"' % (
    'CC', "website", "url", "date", "device", "keyword", "impressions", "clicks", "ctr", "position", "sessions (week)",
    "product")
    ga, gsc = initialize_service(argv, "analytics"), initialize_service(argv, "webmasters")

    for website in GA_IDS[args.cc]:
        if args.pages:
            urls = get_top_landing_pages(ga, args.cc, website, args.date, args.pages)
        else:
            urls = get_urls(args.file)

        bar = Bar('Processing', max=len(urls) if args.file else args.pages, suffix='%(percent).1f%% - %(eta)ds')

        for row in urls:

            data = []
            if args.pages:
                dimensions = ['query', 'date', 'device']
            else:
                dimensions = ""
            data.extend(get_keyword_data(gsc, args.cc, website, args.date, row[0][1:], PROTOCOL[website], dimensions))

            output(args.cc, website, row[0], row[1], data, row[2])

            bar.next()
        bar.finish()

    print >> sys.stderr, '# End: search-console data: %s, %s, %s, %s' % (
    args.cc, args.date, args.pages, datetime.datetime.now().time().isoformat())


if __name__ == '__main__':
    main(sys.argv)
