from __future__ import unicode_literals
import argparse
from elasticsearch import Elasticsearch, helpers
import sys, csv

reload(sys)
sys.setdefaultencoding("UTF-8")

parser = argparse.ArgumentParser(description='Write scraper log to csv file')
parser.add_argument('--date', type=str, required=True, metavar='YYYYMMDD', help='log date (required)')
args = parser.parse_args()

DB = 'http://es-elk.ipricegroup.com:9200'
SCROLL = 10000

FIELDS = ['@timestamp', 'message', 'data.product_id', 'data.store.merchant_id',
    'data.store.url', 'data.old_price', 'data.new_price']

QUERY = {
    "_source": FIELDS,
    "query": {
        "bool": {
            "must": [
                {
                    "terms": {
                        "level.keyword": [
                            "INFO"
                        ]
                    }
                }
            ],
            "must_not": [
                {
                    "terms": {
                        "message.keyword": [
                            "start requesting",
                            "total of all products to crawl"
                        ]
                    }
                }
            ]
        }
    }
}

# flatten nested dictionary into { 'key.subkey.subkey': value, ... }
def flatdict(d, sep='.', prefix=''):
    for k in d:
        if type(d[k]) is dict:
            for p in flatdict(d[k],sep=sep,prefix=prefix+str(k)+sep):
                yield p
        else:
            yield (prefix+str(k),d[k])

if __name__ == '__main__':
    es = Elasticsearch(DB, verify_certs=False)
    response = helpers.scan(es, index="scraper_log_" + args.date, query=QUERY, size=SCROLL, timeout="600s")

    lines = (dict(flatdict(item['_source'], sep='.')) for item in response)

    csv_writer = csv.DictWriter(sys.stdout, fieldnames = FIELDS)
    csv_writer.writeheader()

    csv_writer.writerows(lines)
