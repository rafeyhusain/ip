# run batchfile from cmd:
# get_firstlevel_products_by_category.bat
# get_secondlevel_products_by_category.bat
# change in the batch file how many products you need

# !/usr/bin/env python
# python ES_get_products_by_category.py "Computing" 10000

from datetime import datetime
from elasticsearch import Elasticsearch, RequestsHttpConnection
import csv
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

ES_HOST = 'https://iprice:fGcXoXcBtYaWfUpE@es-qa.ipricegroup.com:443'

try:
    CATEGORY_1 = sys.argv[1]
    # CATEGORY_EXCLUDE = sys.argv[2]
    ITEM_PER_CATEGORY = sys.argv[2]
except IndexError as e:
    print('Usage:')
    print('python export_product_2_csv.py CATEGORY_1 ITEM_PER_CATEGORY')
    # print('country code: vn, my, hk, sg, id, th, ph')
    exit()

try:
    es = Elasticsearch(
        [ES_HOST],
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    country = 'my'
    query = {
        "_source": ["category", "brand", "masterbrain"],
        "size": ITEM_PER_CATEGORY,
        "query": {
            "bool": {
                "must": [
                    {
                        "prefix": {
                            "category.name": {
                                "value": CATEGORY_1

                            }
                        }
                    }
                ],
                "must_not": [
                    {
                        "term": {
                            "masterbrain": {
                                "value": ""
                            }
                        }
                    }
                ],
                "must_not": [
                    {
                        "term": {
                            "brand.name": {
                                "value": ""
                            }
                        }
                    }
                ]
            }
        }
    }

    res = es.search(index="product_" + country, body=query)

    buckets = res['hits']['hits']

    filename = 'pr_' + datetime.today().strftime('%d-%m-%y-%H-%M') + '-' + CATEGORY_1.replace('/', '-') + '.csv'
    f = csv.writer(open(filename, "w"))

    f.writerow([
        "category_prefix",
        "category",
        "masterbrain",
        "brandName",
    ])

    for bucket in buckets:
        product = bucket['_source']

        if 'masterbrain' in product and product['masterbrain'] != '':
            masterbrain = product['masterbrain']
        else:
            continue
        if 'brand' in product and product['brand']['name'] != '':
            brandName = product['brand']['name']
        else:
            continue

        f.writerow([
            CATEGORY_1,
            product['category']['name'],
            masterbrain,
            brandName,
        ])

except Exception as e:
    print (e)
