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
    "size": 2500,
    "query": {
        "match_all": {}
    }
}


def get_data(cc):
    retry = 3
    while retry:
        es = elasticsearch.Elasticsearch(DB, verify_certs=False)

        try:
            res = es.search(index="content_" + cc.lower(), doc_type="productStore", body=QUERY, timeout="600s",
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
    headers = ["CC", "Name", "Image", "DeliveryInfo", "PaymentMethods"]
    for store in query['hits']:
        temp = [cc, store['_source']['name'], store['_source']['image'],
                re.sub('[\r\n]+', '', re.sub('<[^<]+?>', '', store['_source']['deliveryInfo'])),
                ";".join([str(x['name']) for x in store['_source']['paymentMethods']])]
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
