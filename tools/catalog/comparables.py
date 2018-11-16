#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse, datetime, urllib, re, socket, sys, pandas, elasticsearch, urllib3, time, warnings

reload(sys)
sys.setdefaultencoding("UTF-8")
socket.setdefaulttimeout(10)
urllib3.disable_warnings()
warnings.filterwarnings("ignore", ".* using SSL with verify_certs=False is insecure.")

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('cc', type=str, help=('Country code).'))

DB = 'http://es-master.ipricegroup.com:9200'

QUERY = {
    "size": 50000,
    "query": {
        "match_all": {}
    }
}


def get_data(cc):
    retry = 3
    while retry:
        es = elasticsearch.Elasticsearch(DB, verify_certs=False)

        try:
            res = es.search(index="product_" + cc.lower(), doc_type="comparable", body=QUERY,
                            timeout="600s",
                            request_timeout=600)
            return res['hits']
        except elasticsearch.exceptions.AuthorizationException:
            retry = retry - 1
        except elasticsearch.exceptions.ConnectionTimeout:
            retry = retry - 1
            time.sleep(10)

    print >> sys.stderr, "ERROR: Couldn't download data for Stores"
    return None


def output(cc, query):
    array = []

    headers = [
        'country',
        'comparableUrl',
        'comparableType',
        'popularity',
        'category',
        'brand',
        'cheapestMerchant1',
        'cheapestPrice1',
        'cheapestMerchant2',
        'cheapestPrice2',
        'cheapestMerchant3',
        'cheapestPrice3'
    ]

    for c in query['hits']:
        data = c['_source']

        temp = [
            cc,
            data['comparableUrl'],
            data['comparableType'],
            data['popularity'],
            data['category']['url'],
            data['brand']['url'],
            data['cheapestOffers'][0]['store']['merchant_id'] if len(data['cheapestOffers']) > 0 else '',
            data['cheapestOffers'][0]['price']['sale'] if len(data['cheapestOffers']) > 0 else '',
            data['cheapestOffers'][1]['store']['merchant_id'] if len(data['cheapestOffers']) > 1 else '',
            data['cheapestOffers'][1]['price']['sale'] if len(data['cheapestOffers']) > 1 else '',
            data['cheapestOffers'][2]['store']['merchant_id'] if len(data['cheapestOffers']) > 2 else '',
            data['cheapestOffers'][2]['price']['sale'] if len(data['cheapestOffers']) > 2 else '',

        ]
        array.append(temp)

    output = pandas.DataFrame(array, columns=headers)
    output.to_csv(sys.stdout, header=True, index=False, encoding='utf-8-sig')


def main(argv):
    args = argparser.parse_args()

    print >> sys.stderr, '# Start: Store Data: %s, %s' % (
        args.cc, datetime.datetime.now().time().isoformat())

    output(args.cc, get_data(args.cc))

    print >> sys.stderr, '# End: Store Data: %s, %s' % (args.cc, datetime.datetime.now().time().isoformat())


if __name__ == '__main__':
    main(sys.argv)
