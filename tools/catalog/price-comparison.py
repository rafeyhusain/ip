#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse, re, datetime, urllib, socket, sys, pandas, elasticsearch, urllib3, time, warnings

reload(sys)
sys.setdefaultencoding("UTF-8")
socket.setdefaulttimeout(10)
urllib3.disable_warnings()
warnings.filterwarnings("ignore", ".* using SSL with verify_certs=False is insecure.")

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('cc', type=str, help=('Country code).'))

DB = 'http://es-master.ipricegroup.com:9200'
PC_URL = {'my': '/compare/', 'ph': '/compare/', 'sg': '/compare/', 'hk': '/compare/', 'id': '/harga/', 'th': '/ราคา/',
          'vn': '/gia-ban/'}
MAX_SIZE = 10000

QUERY = {
    "size": 0,
    "query": {
        "term": {
            "comparable": True
        }
    },
    "aggs": {
        "brand": {
            "terms": {
                "field": "brand.url",
                "size": MAX_SIZE
            },
            "aggs": {
                "series": {
                    "terms": {
                        "field": "series.url",
                        "size": MAX_SIZE
                    },
                    "aggs": {
                        "model": {
                            "terms": {
                                "field": "model.url",
                                "size": MAX_SIZE
                            },
                            "aggs": {
                                "c1": {
                                    "terms": {
                                        "field": "characteristic.c1.value",
                                        "size": MAX_SIZE
                                    },
                                    "aggs": {
                                        "c2": {
                                            "terms": {
                                                "field": "characteristic.c2.value",
                                                "size": MAX_SIZE
                                            },
                                            "aggs": {
                                                "c3": {
                                                    "terms": {
                                                        "field": "characteristic.c3.value",
                                                        "size": MAX_SIZE
                                                    },
                                                    "aggs": {
                                                        "priceSale": {
                                                            "stats": {
                                                                "field": "priceUsd.sale"
                                                            }
                                                        },
                                                        "priceOrg": {
                                                            "stats": {
                                                                "field": "priceUsd.original"
                                                            }
                                                        },
                                                        "stores": {
                                                            "cardinality": {
                                                                "field": "store.url"
                                                            }
                                                        },
                                                        "cat_store": {
                                                            "top_hits": {
                                                                "_source": {
                                                                    "includes": [
                                                                        "category.name",
                                                                        "store.name"
                                                                    ]
                                                                },
                                                                "size": 1,
                                                                "sort": [
                                                                    {
                                                                        "priceUsd.sale": {
                                                                            "order": "asc"
                                                                        }
                                                                    }
                                                                ]
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                },
                                "priceSale": {
                                    "stats": {
                                        "field": "priceUsd.sale"
                                    }
                                },
                                "priceOrg": {
                                    "stats": {
                                        "field": "priceUsd.original"
                                    }
                                },
                                "stores": {
                                    "cardinality": {
                                        "field": "store.url"
                                    }
                                },
                                "cat_store": {
                                    "top_hits": {
                                        "_source": {
                                            "includes": [
                                                "category.name",
                                                "store.name"
                                            ]
                                        },
                                        "size": 1,
                                        "sort": [
                                            {
                                                "priceUsd.sale": {
                                                    "order": "asc"
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        }
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
            res = es.search(index="product_" + cc.lower(), body=QUERY, timeout="600s", request_timeout=600)
            return res['aggregations']
        except elasticsearch.exceptions.AuthorizationException:
            retry = retry - 1
        except elasticsearch.exceptions.ConnectionTimeout:
            retry = retry - 1
            time.sleep(10)

    print >> sys.stderr, "ERROR: Couldn't download data for price-comparison"
    return None


def output(cc, data):
    headers = ['CC', 'URL', 'Keyword', 'Type', 'Products', 'Merchants', 'Category', 'Brand', 'Series', 'Model',
               'MinPriceSale', 'MaxPriceSale', 'AvgPriceSale', 'MinPriceOrg', 'MaxPriceOrg', 'AvgPriceOrg',
               'CheapestStore']

    array = []
    for brand in data['brand']['buckets']:
        for series in brand['series']['buckets']:
            for model in series['model']['buckets']:
                array += [parse_product(cc, brand, series, model)]
                for c1 in model['c1']['buckets']:
                    for c2 in c1['c2']['buckets']:
                        for c3 in c2['c3']['buckets']:
                            if c3['key'] or c2['key'] or c1['key']:
                                array += [parse_product(cc, brand, series, model, c1, c2, c3)]

    output = pandas.DataFrame(array, columns=headers)
    output.to_csv(sys.stdout, header=True, index=False, encoding='utf-8-sig')


def parse_product(cc, brand, series, model, c1=None, c2=None, c3=None):
    item = []
    item += [cc]
    # brand = model['cat_store']['hits']['hits'][0]['_source']['brand']['url']

    if c3:
        item += [PC_URL[cc] + "-".join(filter(None, [re.sub('[^a-zA-Z\d\s\-]', '', x) for x in
                                                     [brand['key'], series['key'], model['key'], c1['key'], c2['key'],
                                                      c3['key']]])).lower().replace(" ", "-") + "/"]
        item += [(" ".join(filter(None, [re.sub('[^a-zA-Z\d\s\-]', '', x) for x in
                                         [brand['key'], series['key'], model['key'], c1['key'], c2['key'],
                                          c3['key']]])))]
        item += ['variant']
        item += [c3['doc_count']]
        item += [c3['stores']['value']]
        item += [model['cat_store']['hits']['hits'][0]['_source']['category']['name']]
        item += [brand['key']]
        item += [series['key']]
        item += [model['key']]
        item += ["%.2f" % c3['priceSale']['min']]
        item += ["%.2f" % c3['priceSale']['max']]
        item += ["%.2f" % c3['priceSale']['avg']]
        item += ["%.2f" % c3['priceOrg']['min']]
        item += ["%.2f" % c3['priceOrg']['max']]
        item += ["%.2f" % c3['priceOrg']['avg']]
        item += [model['cat_store']['hits']['hits'][0]['_source']['store']['name']]
    else:
        item += [PC_URL[cc] + "-".join(filter(None, [re.sub('[^a-zA-Z\d\s\-]', '', x) for x in
                                                     [brand['key'], series['key'], model['key']]])) + "/"]
        item += [(" ".join(
            filter(None, [re.sub('[^a-zA-Z\d\s\-]', '', x) for x in [brand['key'], series['key'], model['key']]])))]
        item += ['model']
        item += [model['doc_count']]
        item += [model['stores']['value']]
        item += [model['cat_store']['hits']['hits'][0]['_source']['category']['name']]
        item += [brand['key']]
        item += [series['key']]
        item += [model['key']]
        item += ["%.2f" % model['priceSale']['min']]
        item += ["%.2f" % model['priceSale']['max']]
        item += ["%.2f" % model['priceSale']['avg']]
        item += ["%.2f" % model['priceOrg']['min']]
        item += ["%.2f" % model['priceOrg']['max']]
        item += ["%.2f" % model['priceOrg']['avg']]
        item += [model['cat_store']['hits']['hits'][0]['_source']['store']['name']]

    return item


def main(argv):
    args = argparser.parse_args()

    print >> sys.stderr, '# Start: Price Comparison Data: %s, %s' % (
    args.cc, datetime.datetime.now().time().isoformat())

    output(args.cc, get_data(args.cc))

    print >> sys.stderr, '# End: Price Comparison Data: %s, %s' % (args.cc, datetime.datetime.now().time().isoformat())


if __name__ == '__main__':
    main(sys.argv)
