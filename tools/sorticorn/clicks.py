import urllib3
import warnings
import argparse
import elasticsearch
import progressbar
import pandas
from datetime import datetime, timedelta
import sys


def argument_registry():
    parser = argparse.ArgumentParser(__file__, description='Importing relevent product clicks data for sorticorn')
    options_registry(parser)

    return parser


def options_registry(parser):
    default_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    parser.add_argument('--brand', type=str, help='Brand url to fetch from')
    parser.add_argument('--category', type=str, help='Category url to fetch from')
    parser.add_argument('--country', type=str, help='Product country to query from', required=True)
    parser.add_argument('--date', type=str, help='Date for log clicks', default=default_date)


def validate_params(params):
    # Require either brand or category or both
    if params.brand is None and params.category is None:
        raise Exception('Require [--brand] and/or [--category] to be specified')


def importer(brand, category, country, date):
    urllib3.disable_warnings()
    warnings.filterwarnings("ignore", ".* using SSL with verify_certs=False is insecure.")
    client = elasticsearch.Elasticsearch(
        'http://es-master.ipricegroup.com:9200',
        verify_certs=False
    )

    url = '%s/%s' % (brand or '', category or '')

    query = {
        "size": 1000,
        "_source": [
            "exitUrl",
            "created",
            "id",
            "price.sale"
        ],
        "query": {
            "bool": {
                "must": [
                    {
                        "prefix": {
                            "exitUrl": '/' + url.strip('/') + '/'
                        }
                    },
                    {
                        "term": {
                            "created": date
                        }
                    }
                ]
            }
        }
    }

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


def prepare_data(output):
    data = []
    headers = [
        'page',
        'date',
        'listOfProduct',
        'listOfPrices'
    ]

    for item in output:
        tmp = [
            item['_source']['exitUrl'],
            item['_source']['created'],
            item['_source']['id'],
            item['_source']['price']['sale'],
        ]
        data.append(tmp)
    return pandas.DataFrame(data, columns=headers)


if __name__ == '__main__':
    params = argument_registry().parse_args()
    validate_params(params)
    result = importer(params.brand, params.category, params.country, params.date)
    prepare_data(result).to_csv(sys.stdout, index=False, encoding='utf-8')
