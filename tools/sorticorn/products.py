import urllib3
import warnings
import argparse
import elasticsearch
import progressbar
import pandas
import sys


def argument_registry():
    parser = argparse.ArgumentParser(__file__, description='Importing relevent product data for sorticorn')
    options_registry(parser)

    return parser


def options_registry(parser):
    parser.add_argument('--brand', type=str, help='Brand url to fetch from')
    parser.add_argument('--category', type=str, help='Category url to fetch from')
    parser.add_argument('--country', type=str, help='Product country to query from', required=True)
    parser.add_argument('--size', type=int, help='Record size to fetch', default=1000)
    parser.add_argument('--days', type=str, help='No of days for log clicks', default=30)


def validate_params(params):
    # Require either brand or category or both
    if params.brand is None and params.category is None:
        raise Exception('Require [--brand] and/or [--category] to be specified')


def importer(brand, category, size, country):
    urllib3.disable_warnings()
    warnings.filterwarnings("ignore", ".* using SSL with verify_certs=False is insecure.")

    client = elasticsearch.Elasticsearch(
        'http://es-master.ipricegroup.com:9200',
        verify_certs=False
    )

    query = {
        "size": 1000,
        "_source": [
            "name",
            "description",
            "images",
            "brand.name",
            "series.name",
            "model.name",
            "gender",
            "category.name",
            "price.original",
            "price.sale",
            "listingDate",
            "store",
            "popularity",
            "color",
            "gender",
        ],
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "comparable": "false"
                        }
                    }
                ]
            }
        },
        "sort": [
            {
                "popularity": {
                    "order": "desc"
                }
            }
        ]
    }

    if category is not None:
        query["query"]["bool"]["must"].append({
            "prefix": {
                "category.url": category
            }
        })

    if brand is not None:
        query["query"]["bool"]["must"].append({
            "term": {
                "brand.url": brand
            }
        })

    response = client.search(
        index='product_{}'.format(country),
        body=query,
        doc_type='product',
        scroll='15m'
    )

    output = []

    output.extend(response['hits']['hits'])
    scroll_id = response['_scroll_id']
    total = response['hits']['total']
    fetched = len(response['hits']['hits'])
    limit = min(size, total)

    if total > 0:
        bar = progressbar.ProgressBar(maxval=limit)
        bar.start()
        while fetched < limit:
            response = client.scroll(scroll_id=scroll_id, scroll='2m')
            output.extend(response['hits']['hits'])
            scroll_id = response['_scroll_id']
            fetched += len(response['hits']['hits'])
            bar.update(fetched)
        bar.finish()

        return output
    else:
        raise Exception('No listing found!')


def prepare_data(output, log_data):
    data = []
    headers = [
        'id',
        'name',
        'images',
        'description',
        'brand',
        'series',
        'model',
        'category',
        'price',
        'priceSale',
        'age',
        'merchant',
        'popularity',
        'color',
        'gender',
        'clicks',
    ]

    for item in output:
        clicks = log_data.get(item['_id']) if item['_id'] in log_data else 0
        tmp = [
            item['_id'],
            item['_source']['name'],
            item['_source']['images'][0]['s3Url'],
            item['_source']['description'],
            item['_source']['brand']['name'],
            item['_source']['series']['name'],
            item['_source']['model']['name'],
            item['_source']['category']['name'],
            item['_source']['price']['original'],
            item['_source']['price']['sale'],
            item['_source']['listingDate'],
            item['_source']['store']['name'],
            item['_source']['popularity'],
            item['_source']['color'],
            item['_source']['gender'],
            clicks,
        ]
        data.append(tmp)
    return pandas.DataFrame(data, columns=headers)


def get_log_data(brand, category, country, days):
    query = {
        "size": 1000,
        "_source": ["id"],
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "created": {
                                "gte": 'now-' + str(days) + 'd/d'
                            }
                        }
                    }
                ]
            }
        }
    }

    if category is not None:
        query["query"]["bool"]["must"].append({
            "prefix": {
                "category.url": category
            }
        })

    if brand is not None:
        query["query"]["bool"]["must"].append({
            "term": {
                "brand.url": brand
            }
        })

    client = elasticsearch.Elasticsearch('http://es-master.ipricegroup.com:9200', verify_certs=False)
    response = client.search(
        index='log_{}'.format(country),
        body=query,
        doc_type='product',
        scroll='15m'
    )
    output = []
    output.extend(response['hits']['hits'])
    scroll_id = response['_scroll_id']
    total = response['hits']['total']
    fetched = len(response['hits']['hits'])
    if total > 0:
        bar = progressbar.ProgressBar(maxval=total)
        bar.start()
        while fetched < total:
            response = client.scroll(scroll_id=scroll_id, scroll='2m')
            output.extend(response['hits']['hits'])
            scroll_id = response['_scroll_id']
            fetched += len(response['hits']['hits'])
            bar.update(fetched)
        bar.finish()
        return output
    else:
        raise Exception('No listing found!')


def prepare_log_data(output):
    data = {}

    for item in output:
        product_id = item['_source']['id']
        if product_id in data:
            data[product_id] += 1
        else:
            data[product_id] = 1

    return data


if __name__ == '__main__':
    params = argument_registry().parse_args()
    validate_params(params)

    log_data = prepare_log_data(get_log_data(params.brand, params.category, params.country, params.days))

    result = importer(params.brand, params.category, params.size, params.country)
    prepare_data(result, log_data).to_csv(sys.stdout, index=False, encoding='utf-8')
