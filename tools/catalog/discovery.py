#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse, datetime, elasticsearch, pandas, urllib, urllib3, socket, string, sys, time, warnings

GENDER = {'my': {0: '', 1: 'men', 2: 'women'},
          'hk': {0: '', 1: 'men', 2: 'women'},
          'ph': {0: '', 1: 'men', 2: 'women'},
          'sg': {0: '', 1: 'men', 2: 'women'},
          'id': {0: '', 1: 'pria', 2: 'wanita'},
          'vn': {0: '', 1: ' Nam', 2: 'Nữ'},
          'th': {0: '', 1: 'ผู้ชาย', 2: 'ผู้หญิง'}}
GENDER_DATA = {'': '', 0: '', 1: 'men', 2: 'women'}
DOC_MIN_COUNT = 15
reload(sys)
sys.setdefaultencoding("UTF-8")
socket.setdefaulttimeout(10)
urllib3.disable_warnings()
warnings.filterwarnings("ignore", ".* using SSL with verify_certs=False is insecure.")

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('cc', type=str, help=('Country code).'))

DB = 'http://es-master.ipricegroup.com:9200'
MAX_SIZE = 100000

BRAND_QUERY = {
    "size": 0,
    "query": {
        "prefix": {"brand.url": "a"}
    },
    "aggs": {
        "brand": {
            "terms": {
                "size": MAX_SIZE,
                "exclude": [""],
                "min_doc_count": DOC_MIN_COUNT,
                "field": "brand.url"
            },
            "aggs": {
                "basketsize": {
                    "avg": {
                        "field": "priceUsd.sale"
                    }
                },
                "pc-products": {
                    "filter": {
                        "term": {
                            "_type": "comparable",
                        }
                    }
                },
                "pc-offers": {
                    "filter": {
                        "term": {
                            "comparable": "true",
                        }
                    }
                },
                "series": {
                    "terms": {
                        "size": MAX_SIZE,
                        "exclude": [""],
                        "min_doc_count": DOC_MIN_COUNT,
                        "field": "series.url"
                    },
                    "aggs": {
                        "basketsize": {
                            "avg": {
                                "field": "priceUsd.sale"
                            }
                        },
                        "pc-products": {
                            "filter": {
                                "term": {
                                    "_type": "comparable",
                                }
                            }
                        },
                        "pc-offers": {
                            "filter": {
                                "term": {
                                    "comparable": "true",
                                }
                            }
                        },
                        "model": {
                            "terms": {
                                "size": MAX_SIZE,
                                "exclude": [""],
                                "min_doc_count": DOC_MIN_COUNT,
                                "field": "model.url"
                            },
                            "aggs": {
                                "basketsize": {
                                    "avg": {
                                        "field": "priceUsd.sale"
                                    }
                                },
                                "pc-products": {
                                    "filter": {
                                        "term": {
                                            "_type": "comparable",
                                        }
                                    }
                                },
                                "pc-offers": {
                                    "filter": {
                                        "term": {
                                            "comparable": "true",
                                        }
                                    }
                                },
                                "category": {
                                    "terms": {
                                        "size": MAX_SIZE,
                                        "exclude": [""],
                                        "min_doc_count": DOC_MIN_COUNT,
                                        "field": "category.url"
                                    },
                                    "aggs": {
                                        "basketsize": {
                                            "avg": {
                                                "field": "priceUsd.sale"
                                            }
                                        },
                                        "pc-products": {
                                            "filter": {
                                                "term": {
                                                    "_type": "comparable",
                                                }
                                            }
                                        },
                                        "pc-offers": {
                                            "filter": {
                                                "term": {
                                                    "comparable": "true",
                                                }
                                            }
                                        },
                                        "gender": {
                                            "terms": {
                                                "size": MAX_SIZE,
                                                "exclude": [0],
                                                "min_doc_count": DOC_MIN_COUNT,
                                                "field": "gender"
                                            },
                                            "aggs": {
                                                "basketsize": {
                                                    "avg": {
                                                        "field": "priceUsd.sale"
                                                    }
                                                },
                                                "pc-products": {
                                                    "filter": {
                                                        "term": {
                                                            "_type": "comparable",
                                                        }
                                                    }
                                                },
                                                "pc-offers": {
                                                    "filter": {
                                                        "term": {
                                                            "comparable": "true",
                                                        }
                                                    }
                                                },
                                            }
                                        },
                                        "cat_name": {
                                            "top_hits": {
                                                "_source": [
                                                    "category.name"
                                                ],
                                                "size": 1
                                            }
                                        }
                                    }
                                },
                                "gender": {
                                    "terms": {
                                        "field": "gender",
                                        "exclude": [0],
                                        "min_doc_count": DOC_MIN_COUNT,
                                        "size": MAX_SIZE
                                    },
                                    "aggs": {
                                        "basketsize": {
                                            "avg": {
                                                "field": "priceUsd.sale"
                                            }
                                        },
                                        "pc-products": {
                                            "filter": {
                                                "term": {
                                                    "_type": "comparable",
                                                }
                                            }
                                        },
                                        "pc-offers": {
                                            "filter": {
                                                "term": {
                                                    "comparable": "true",
                                                }
                                            }
                                        },
                                    }
                                },
                                "model_name": {
                                    "top_hits": {
                                        "_source": [
                                            "model.name"
                                        ],
                                        "size": 1
                                    }
                                }
                            }
                        },
                        "category": {
                            "terms": {
                                "size": MAX_SIZE,
                                "min_doc_count": DOC_MIN_COUNT,
                                "field": "category.url"
                            },
                            "aggs": {
                                "basketsize": {
                                    "avg": {
                                        "field": "priceUsd.sale"
                                    }
                                },
                                "pc-products": {
                                    "filter": {
                                        "term": {
                                            "_type": "comparable",
                                        }
                                    }
                                },
                                "pc-offers": {
                                    "filter": {
                                        "term": {
                                            "comparable": "true",
                                        }
                                    }
                                },
                                "gender": {
                                    "terms": {
                                        "field": "gender",
                                        "exclude": [0],
                                        "size": MAX_SIZE,
                                        "min_doc_count": DOC_MIN_COUNT
                                    },
                                    "aggs": {
                                        "basketsize": {
                                            "avg": {
                                                "field": "priceUsd.sale"
                                            }
                                        },
                                        "pc-products": {
                                            "filter": {
                                                "term": {
                                                    "_type": "comparable",
                                                }
                                            }
                                        },
                                        "pc-offers": {
                                            "filter": {
                                                "term": {
                                                    "comparable": "true",
                                                }
                                            }
                                        },
                                    }
                                },
                                "cat_name": {
                                    "top_hits": {
                                        "_source": "category.name",
                                        "size": 1
                                    }
                                }
                            }
                        },
                        "gender": {
                            "terms": {
                                "size": MAX_SIZE,
                                "field": "gender",
                                "exclude": [0],
                                "min_doc_count": DOC_MIN_COUNT
                            },
                            "aggs": {
                                "basketsize": {
                                    "avg": {
                                        "field": "priceUsd.sale"
                                    }
                                },
                                "pc-products": {
                                    "filter": {
                                        "term": {
                                            "_type": "comparable",
                                        }
                                    }
                                },
                                "pc-offers": {
                                    "filter": {
                                        "term": {
                                            "comparable": "true",
                                        }
                                    }
                                },
                            }
                        },
                        "series_name": {
                            "top_hits": {
                                "_source": "series.name",
                                "size": 1
                            }
                        }
                    }
                },
                "category": {
                    "terms": {
                        "size": MAX_SIZE,
                        "min_doc_count": DOC_MIN_COUNT,
                        "field": "category.url"
                    },
                    "aggs": {
                        "basketsize": {
                            "avg": {
                                "field": "priceUsd.sale"
                            }
                        },
                        "pc-products": {
                            "filter": {
                                "term": {
                                    "_type": "comparable",
                                }
                            }
                        },
                        "pc-offers": {
                            "filter": {
                                "term": {
                                    "comparable": "true",
                                }
                            }
                        },
                        "gender": {
                            "terms": {
                                "size": MAX_SIZE,
                                "exclude": [0],
                                "field": "gender",
                                "min_doc_count": DOC_MIN_COUNT
                            },
                            "aggs": {
                                "basketsize": {
                                    "avg": {
                                        "field": "priceUsd.sale"
                                    }
                                },
                                "pc-products": {
                                    "filter": {
                                        "term": {
                                            "_type": "comparable",
                                        }
                                    }
                                },
                                "pc-offers": {
                                    "filter": {
                                        "term": {
                                            "comparable": "true",
                                        }
                                    }
                                },
                            }
                        },
                        "cat_name": {
                            "top_hits": {
                                "_source": "category.name",
                                "size": 1
                            }
                        }
                    }
                },
                "gender": {
                    "terms": {
                        "field": "gender",
                        "min_doc_count": DOC_MIN_COUNT,
                        "exclude": [0],
                        "size": MAX_SIZE
                    },
                    "aggs": {
                        "basketsize": {
                            "avg": {
                                "field": "priceUsd.sale"
                            }
                        },
                        "pc-products": {
                            "filter": {
                                "term": {
                                    "_type": "comparable",
                                }
                            }
                        },
                        "pc-offers": {
                            "filter": {
                                "term": {
                                    "comparable": "true",
                                }
                            }
                        },
                    }
                },
                "brand_name": {
                    "top_hits": {
                        "_source": [
                            "brand.name"
                        ],
                        "size": 1
                    }
                }
            }
        }
    }
}

CATEGORY_QUERY = {
    "size": 0,
    "query": {
        "match_all": {}
    },
    "aggs": {
        "category": {
            "terms": {
                "field": "category.url",
                "size": MAX_SIZE
            },
            "aggs": {
                "basketsize": {
                    "avg": {
                        "field": "priceUsd.sale"
                    }
                },
                "gender": {
                    "terms": {
                        "field": "gender",
                        "min_doc_count": DOC_MIN_COUNT,
                        "exclude": [
                            "0"
                        ],
                        "size": 1
                    },
                    "aggs": {
                        "basketsize": {
                            "avg": {
                                "field": "priceUsd.sale"
                            }
                        },
                        "pc-products": {
                            "filter": {
                                "term": {
                                    "_type": "comparable",
                                }
                            }
                        },
                        "pc-offers": {
                            "filter": {
                                "term": {
                                    "comparable": "true",
                                }
                            }
                        },
                        "cat_name": {
                            "top_hits": {
                                "_source": [
                                    "category.name"
                                ],
                                "size": 1
                            }
                        }
                    }
                },
                "pc-products": {
                    "filter": {
                        "term": {
                            "_type": "comparable",
                        }
                    }
                },
                "pc-offers": {
                    "filter": {
                        "term": {
                            "comparable": "true",
                        }
                    }
                },
                "cat_name": {
                    "top_hits": {
                        "_source": [
                            "category.name"
                        ],
                        "size": 1
                    }
                }
            }
        }
    }
}


def get_data(cc, query):
    retry = 3
    while retry:
        es = elasticsearch.Elasticsearch(DB, verify_certs=False)

        try:
            res = es.search(index="product_" + cc.lower(), body=query, timeout="600s", request_timeout=600)
            return res['aggregations']
        except elasticsearch.exceptions.AuthorizationException:
            retry = retry - 1
        except elasticsearch.exceptions.ConnectionTimeout:
            retry = retry - 1
            time.sleep(10)

    print >> sys.stderr, "ERROR: Couldn't download data"
    return None


def create_url(cc, brand='', series='', model='', category='', gender=0):
    gender = GENDER[cc][gender]
    url = []
    if sum(x == '' for x in [brand, series, model, category]) != 0:
        url = [brand, series, model, category, gender]
    else:
        split_category = category.split('/')
        category = [split_category[0], gender] + ['/'.join(split_category[1:])] if len(split_category) >= 1 else []
        url = [brand, series, model] + category
    return '/' + '/'.join([x for x in url if x != '']) + '/'


def create_header_keyword(cc, brand='', series='', model='', category='', gender=0):
    gender = GENDER[cc][gender]
    params = [x.split('/')[-1] if '/' in x else x for x in [brand, series, model, category, gender]]
    headers = [x for x in params if x != '']
    keyword = ' '.join(headers)
    return keyword.lower()


def create_data_dict(product, basketsize, type, brand={'key': '', 'name': ''}, series={'key': '', 'name': ''},
                     model={'key': '', 'name': ''}, category={'key': '', 'name': ''}, gender=0, pc=0, offers=0):
    item = {"type": type, "brand": brand, "series": series, "model": model, "category": category, "gender": gender,
            "product": product, "basketsize": basketsize, "pc": pc, "offers": offers}
    return item


def output(cc, data):
    output = []
    headers = ['CC', 'Brand', 'Series', 'Model', 'Category', 'Gender', 'URL', 'Offers', 'Keyword',
               'BasketSize', 'Type', 'PC Products', 'PC Offers']
    for item in data:
        temp = [cc,
                item['brand']['key'],
                item['series']['key'],
                item['model']['key'],
                item['category']['key'],
                GENDER_DATA[item['gender']],
                create_url(cc, item['brand']['key'], item['series']['key'], item['model']['key'],
                           item['category']['key'], item['gender']),
                item['product'],
                create_header_keyword(cc, item['brand']['name'], item['series']['name'], item['model']['name'],
                                      item['category']['name'], item['gender']),
                item['basketsize'],
                item['type'],
                item['pc'],
                item['offers']]
        output.append(temp)
    output_dataframe = pandas.DataFrame(output, columns=headers).drop_duplicates()
    output_dataframe.to_csv(sys.stdout, header=True, index=False, encoding='utf-8-sig')


def parse_data(data):
    array = []
    for thing, aggs in data.iteritems():
        if aggs:
            if thing == 'categories':
                for category in aggs['category']['buckets']:
                    # add main category
                    category_k = {'key': category['key'],
                                  'name': category['cat_name']['hits']['hits'][0]['_source']['category']['name']}
                    array.append(
                        create_data_dict(category['doc_count'], category['basketsize']['value'], category=category_k,
                                         type='category', pc=category['pc-products']['doc_count'],
                                         offers=category['pc-offers']['doc_count']))
                    # add category/gender
                    for gender in category['gender']['buckets']:
                        if len(gender) > 0:
                            array.append(create_data_dict(gender['doc_count'], gender['basketsize']['value'],
                                                          category=category_k, gender=gender['key'],
                                                          type='category-gender', pc=gender['pc-products']['doc_count'],
                                                          offers=gender['pc-offers']['doc_count']))
            if thing == 'brands':
                for brand in aggs['brand']['buckets']:
                    # skip emtpy buckets
                    # add main brand
                    brand_k = {'key': brand['key'],
                               'name': brand['brand_name']['hits']['hits'][0]['_source']['brand']['name']}
                    array.append(
                        create_data_dict(brand['doc_count'], brand['basketsize']['value'], type='brand', brand=brand_k,
                                         pc=brand['pc-products']['doc_count'], offers=brand['pc-offers']['doc_count']))
                    # add brand/series
                    for series in brand['series']['buckets']:

                        series_k = {'key': series['key'],
                                    'name': series['series_name']['hits']['hits'][0]['_source']['series']['name']}
                        array.append(
                            create_data_dict(series['doc_count'], series['basketsize']['value'], type='brand-series',
                                             brand=brand_k, series=series_k, pc=series['pc-products']['doc_count'],
                                             offers=series['pc-offers']['doc_count']))
                        # add brand/series/model
                        for model in series['model']['buckets']:
                            model_k = {'key': model['key'],
                                       'name': model['model_name']['hits']['hits'][0]['_source']['model']['name']}
                            array.append(create_data_dict(model['doc_count'], model['basketsize']['value'],
                                                          type='brand-series-model', brand=brand_k, series=series_k,
                                                          model=model_k, pc=model['pc-products']['doc_count'],
                                                          offers=model['pc-offers']['doc_count']))
                            # add brand/series/model/category
                            for category in model['category']['buckets']:
                                category_k = {'key': category['key'],
                                              'name': category['cat_name']['hits']['hits'][0]['_source']['category'][
                                                  'name']}
                                array.append(create_data_dict(category['doc_count'], category['basketsize']['value'],
                                                              type='brand-series-model-category', brand=brand_k,
                                                              series=series_k, model=model_k, category=category_k,
                                                              pc=category['pc-products']['doc_count'],
                                                              offers=category['pc-offers']['doc_count']))
                                # add brand/series/model/category/gender/
                                for gender in category['gender']['buckets']:
                                    gender_k = gender['key']
                                    array.append(
                                        create_data_dict(gender['doc_count'], gender['basketsize']['value'],
                                                         type='brand-series-model-category-gender', brand=brand_k,
                                                         series=series_k, model=model_k, category=category_k,
                                                         gender=gender_k, pc=gender['pc-products']['doc_count'],
                                                         offers=gender['pc-offers']['doc_count']))
                            for gender in model['gender']['buckets']:
                                array.append(create_data_dict(gender['doc_count'], gender['basketsize']['value'],
                                                              type='brand-series-model-gender', brand=brand_k,
                                                              series=series_k, model=model_k, gender=gender['key'],
                                                              pc=gender['pc-products']['doc_count'],
                                                              offers=gender['pc-offers']['doc_count']))
                        # when series is available but there is no model
                        for category in series['category']['buckets']:
                            category_k = {'key': category['key'], 'name':
                                category['cat_name']['hits']['hits'][0]['_source']['category']['name'].split('/')[
                                    len(category['key'].split('/')) - 1]}
                            array.append(
                                create_data_dict(category['doc_count'], category['basketsize']['value'],
                                                 type='brand-series-category', brand=brand_k, series=series_k,
                                                 category=category_k, pc=category['pc-products']['doc_count'],
                                                 offers=category['pc-offers']['doc_count']))
                            for gender in category['gender']['buckets']:
                                array.append(create_data_dict(gender['doc_count'], gender['basketsize']['value'],
                                                              type='brand-series-category-gender', brand=brand_k,
                                                              series=series_k, category=category_k,
                                                              gender=gender['key'],
                                                              pc=gender['pc-products']['doc_count'],
                                                              offers=gender['pc-offers']['doc_count']))
                        for gender in series['gender']['buckets']:
                            array.append(create_data_dict(gender['doc_count'], gender['basketsize']['value'],
                                                          type='brand-series-gender', brand=brand_k, series=series_k,
                                                          gender=gender['key'], pc=gender['pc-products']['doc_count'],
                                                          offers=gender['pc-offers']['doc_count']))
                    # when series, model are empty
                    for category in brand['category']['buckets']:
                        category_k = {'key': category['key'], 'name':
                            category['cat_name']['hits']['hits'][0]['_source']['category']['name'].split('/')[
                                len(category['key'].split('/')) - 1]}
                        array.append(create_data_dict(category['doc_count'], category['basketsize']['value'],
                                                      type='brand-category', brand=brand_k, category=category_k,
                                                      pc=category['pc-products']['doc_count'],
                                                      offers=category['pc-offers']['doc_count']))
                        for gender in category['gender']['buckets']:
                            array.append(create_data_dict(gender['doc_count'], gender['basketsize']['value'],
                                                          type='brand-category-gender', brand=brand_k,
                                                          category=category_k, gender=gender['key'],
                                                          pc=gender['pc-products']['doc_count'],
                                                          offers=gender['pc-offers']['doc_count']))
                    for gender in brand['gender']['buckets']:
                        gender_k = gender['key']
                        array.append(
                            create_data_dict(gender['doc_count'], gender['basketsize']['value'], type='brand-gender',
                                             brand=brand_k, gender=gender_k, pc=gender['pc-products']['doc_count'],
                                             offers=gender['pc-offers']['doc_count']))
    return array


def main(argv):
    args = argparser.parse_args()
    # start= datetime.datetime.now()
    print >> sys.stderr, '# Start: Discovery Data: %s, %s' % (args.cc, datetime.datetime.now().time().isoformat())

    data = dict()
    data['categories'] = get_data(args.cc, CATEGORY_QUERY)
    data['brands'] = {}
    data['brands']['brand'] = {}
    data['brands']['brand']['buckets'] = []

    # quirk to get the data in segments, while waiting for 5.2 with official partitioning support for aggregations
    for fchar in string.lowercase + "".join(str(x) for x in range(0, 10)):
        for schar in string.lowercase + "".join(str(x) for x in range(0, 10)):
            query = BRAND_QUERY
            query['query']['prefix']['brand.url'] = fchar + schar
            data['brands']['brand']['buckets'].extend(get_data(args.cc, query)['brand']['buckets'])

    data = parse_data(data)
    output(args.cc, data)
    # end = datetime.datetime.now()
    # print "separated time is: "+str((end-start).seconds)
    print >> sys.stderr, '# End: Discovery Data: %s, %s' % (args.cc, datetime.datetime.now().time().isoformat())


if __name__ == '__main__':
    main(sys.argv)
