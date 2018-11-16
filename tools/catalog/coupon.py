#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse, datetime, urllib, socket, sys, pandas, elasticsearch, urllib3, time, warnings

COUPON = {'my': 'coupon', 'ph': 'coupon', 'hk': 'coupon', 'sg': 'coupon', 'id': 'kupon', 'th': 'คูปอง', 'vn': 'coupon'}
reload(sys)
sys.setdefaultencoding("UTF-8")
socket.setdefaulttimeout(10)
urllib3.disable_warnings()
warnings.filterwarnings("ignore", ".* using SSL with verify_certs=False is insecure.")

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('cc', type=str, help=('Country code).'))

DB = 'http://es-master.ipricegroup.com:9200'
MAX_SIZE = 100000

QUERY = {
    "size": 0,
    "query": {
        "match_all": {}
    },
    "aggs": {
        "store": {
            "terms": {
                "field": "store.url",
                "size": MAX_SIZE
            },
            "aggs": {
                "store-name": {
                    "terms": {
                        "field": "store.name",
                        "size": MAX_SIZE
                    }
                },
                "detail": {
                    "top_hits": {
                        "_source": {
                            "includes": ["store.name", "store.url"]
                        },
                        "size": 1
                    }
                }
            }
        }
    }
}


def get_data(cc):
    retry = 3
    while retry:
        es = elasticsearch.Elasticsearch(DB, verify_certs=False)

        try:
            res = es.search(index="content_" + cc.lower(), body=QUERY, timeout="600s",
                            request_timeout=600)
            return res['aggregations']
        except elasticsearch.exceptions.AuthorizationException:
            retry = retry - 1
        except elasticsearch.exceptions.ConnectionTimeout:
            retry = retry - 1
            time.sleep(10)

    print >> sys.stderr, "ERROR: Couldn't download data for Coupon"
    return None


def output(cc, query):
    array = []
    headers = ["CC", "URL", "Keyword", "Coupons (Active+Non-Active)", "Merchant"]
    for store in query['store']['buckets']:
        detail = store['detail']['hits']['hits'][0]['_source']["store"]
        keyword = ''
        if cc == 'id':
            keyword = COUPON[cc] + ' ' + detail['name'].lower()
        else:
            keyword = detail['name'].lower() + ' ' + COUPON[cc]
        temp = [cc, "/coupons/" + detail['url'] + "/", keyword, store['detail']['hits']['total'], detail['url']]
        array.append(temp)
    output = pandas.DataFrame(array, columns=headers)
    output.to_csv(sys.stdout, header=True, index=False, encoding='utf-8-sig')


def main(argv):
    args = argparser.parse_args()

    print >> sys.stderr, '# Start: Coupon Data: %s, %s' % (
        args.cc, datetime.datetime.now().time().isoformat())

    output(args.cc, get_data(args.cc))

    print >> sys.stderr, '# End: Coupon Data: %s, %s' % (args.cc, datetime.datetime.now().time().isoformat())


if __name__ == '__main__':
    main(sys.argv)
