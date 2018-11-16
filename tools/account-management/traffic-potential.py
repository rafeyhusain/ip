#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse, codecs, datetime, socket, sys, urlparse, time, warnings, pandas
import elasticsearch, urllib3, requests

reload(sys)
sys.setdefaultencoding("UTF-8")
socket.setdefaulttimeout(10)
urllib3.disable_warnings()
warnings.filterwarnings("ignore", ".* using SSL with verify_certs=False is insecure.")

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('cc', type=str, help=('Country code).'))
argparser.add_argument('ga', type=argparse.FileType('r'), help=(''))

DB = 'http://es-master.ipricegroup.com:9200'

QUERY_MERCHANTS = {
    "size": 0,
    "query": {
        "match_all": {}
    },
    "aggs": {
        "buckets": {
            "terms": {
                "field": "store.url",
                "size": 100000
            }
        }
    }
}

QUERY_AGGREGATIONS = {
    "size": 0,
    "query": {
        "term": {
            "store.url": "XXX"
        }
    },
    "aggs": {
        "buckets": {
            "terms": {
                "field": "XXX",
                "min_doc_count": 15,
                "size": 100000
            }
        }
    }
}


def get_data(cc, query):
    retry = 3
    while retry:
        es = elasticsearch.Elasticsearch(DB, verify_certs=False)

        try:
            return es.search(index="product_" + cc.lower(), body=query, timeout="600s", request_timeout=600)
        except elasticsearch.exceptions.AuthorizationException:
            retry = retry - 1
        except elasticsearch.exceptions.ConnectionTimeout:
            retry = retry - 1
            time.sleep(10)

    print >> sys.stderr, "ERROR: Couldn't download data"
    return None


def read_merchants(cc):
    # return ["lazada"]

    data = get_data(cc, QUERY_MERCHANTS)

    buckets = []
    for bucket in data['aggregations']['buckets']['buckets']:
        buckets.append(bucket['key'].strip("/").decode("utf8"))

    return buckets


def read_brands(cc, merchant):
    # with codecs.open("input/brands-test.txt", "r", "utf-8") as data_file:
    #   return [x.strip().strip("/") for x in data_file.readlines()]

    query = QUERY_AGGREGATIONS
    query['query']['term']['store.url'] = merchant
    query['aggs']['buckets']['terms']['field'] = "brand.url"
    data = get_data(cc, query)

    buckets = []
    for bucket in data['aggregations']['buckets']['buckets']:
        buckets.append(bucket['key'].strip("/").decode("utf8"))

    return buckets


def read_categories(cc, merchant):
    # with codecs.open("input/categories-test.txt", "r", "utf-8") as data_file:
    #   return [x.strip().strip("/") for x in data_file.readlines()]

    query = QUERY_AGGREGATIONS
    query['query']['term']['store.url'] = merchant
    query['aggs']['buckets']['terms']['field'] = "category.url"
    data = get_data(cc, query)

    buckets = []
    for bucket in data['aggregations']['buckets']['buckets']:
        buckets.append(bucket['key'].strip("/").decode("utf8"))

    return buckets


def read_google_analytics(cc, reader):
    csv = pandas.read_csv(reader)

    pages = {}
    for index, line in csv.iterrows():
        if line['ipg:cc'].lower() == cc.lower():
            if line['ipg:subProduct'] not in pages:
                pages[line['ipg:subProduct']] = {}
            pages[line['ipg:subProduct']][unicode(line['ga:landingPagePath'].strip("/"))] = line['ga:sessions']

    return pages


def main(argv):
    args = argparser.parse_args()

    print >> sys.stderr, '# Start: Merchant Revenue Potential: %s, %s' % (
    args.cc, datetime.datetime.now().time().isoformat())

    data = []
    headers = ['Country', 'Merchant', 'Total Sessions', 'Brand Sessions', 'Category Sessions',
               "Brand-Category Sessions"]

    traffic = read_google_analytics(args.cc, args.ga)
    merchants = read_merchants(args.cc)
    for merchant in merchants:
        brands = read_brands(args.cc, merchant)
        categories = read_categories(args.cc, merchant)

        tb = 0
        tc = 0
        tbc = 0

        for brand in brands:
            if brand in traffic['brand']:
                tb = tb + traffic['brand'][brand]

        for category in categories:
            if category in traffic['category']:
                tc = tc + traffic['category'][category]

        for brand in brands:
            for category in categories:
                key = brand + "/" + category
                if key in traffic['brand-category']:
                    tbc = tbc + traffic['brand-category'][key]

        data.append([args.cc, merchant, tb + tc + tbc, tb, tc, tbc])

    output = pandas.DataFrame(data, columns=headers).drop_duplicates()
    output.to_csv(sys.stdout, header=True, index=False, encoding='utf-8-sig')

    print >> sys.stderr, '# End:  Merchant Revenue Potential: %s, %s' % (
    args.cc, datetime.datetime.now().time().isoformat())


if __name__ == '__main__':
    main(sys.argv)
