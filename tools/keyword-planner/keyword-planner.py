#!/usr/bin/python

import argparse, codecs, datetime, pandas, sys, os, time
import suds, httplib, pprint
from sklearn.feature_extraction.text import CountVectorizer
from googleads import adwords
from progress.bar import Bar

reload(sys)
sys.setdefaultencoding("UTF-8")

COUNTRYCODES = {'MY': '2458', 'TH': '2764', 'ID': '2360', 'HK': '2344', 'SG': '2702', 'PH': '2608', 'VN': '2704'}

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('cc', type=str, help=('Country code(s).'))
argparser.add_argument('--stats', dest="stats", action='store_const', const=1, help=('Return keyword search volume.'))
argparser.add_argument('--ideas', dest="ideas", action='store_const', const=1, help=('Return keyword ideas.'))
argparser.add_argument('--tokenize', type=bool, help=('Tokenize each line of the input files into n-grams.'))
argparser.add_argument('--shingles', type=int, default=0, help=('Number of shingles.'))
argparser.add_argument('file', type=str, help=('File with one keyword per line.'))

PAGE_SIZE = 700


def query_adwords(service, ccs, keywords, rtype):
    data = {}

    retries = 3
    while retries > 0:

        selector = {
            'searchParameters': [
                {
                    'xsi_type': 'RelatedToQuerySearchParameter',
                    'queries': keywords
                },
                {
                    'xsi_type': 'LocationSearchParameter',
                    'locations': [{'id': COUNTRYCODES[cc.upper()]} for cc in ccs]
                },
                {
                    'xsi_type': 'NetworkSearchParameter',
                    'networkSetting': {
                        'targetGoogleSearch': True,
                        'targetSearchNetwork': False,
                        'targetContentNetwork': False,
                        'targetPartnerSearchNetwork': False
                    }
                }
            ],
            'ideaType': 'KEYWORD',
            'requestType': rtype,
            'requestedAttributeTypes': ['KEYWORD_TEXT', 'SEARCH_VOLUME', 'COMPETITION', 'AVERAGE_CPC',
                                        'TARGETED_MONTHLY_SEARCHES', 'CATEGORY_PRODUCTS_AND_SERVICES'],
            'paging': {
                'startIndex': str(0),
                'numberResults': str(PAGE_SIZE)
            },
            'currencyCode': 'USD'
        }

        try:
            data = service.get(selector)
        except suds.WebFault as e:
            if e.fault.faultstring == "[RateExceededError <rateName=RATE_LIMIT, rateKey=null, rateScope=ACCOUNT, retryAfterSeconds=30>]":
                retries = retries - 1
                pprint.pprint("WARNING: RateExceededError, sleeping 30 seconds, retries left #" + str(retries),
                              sys.stderr)
                time.sleep(30)
                continue
        except httplib.BadStatusLine as e:
            pprint.pprint(e, sys.stderr)

        retries = 0

    return data


def initialize_service():
    yaml_path = os.path.join(os.path.dirname(__file__), os.pardir, 'keyword-planner', 'googleads.yaml')
    client = adwords.AdWordsClient.LoadFromStorage(yaml_path)
    service = client.GetService('TargetingIdeaService')
    return service


def parse(cc, data):
    entries = []
    if 'entries' in data:
        for result in data['entries']:
            entry = {}
            entry['cc'] = cc
            entry['cat'] = 'Unknown'

            for attribute in result['data']:
                if attribute['key'] == 'KEYWORD_TEXT':
                    if 'value' in attribute['value']:
                        entry['keyword'] = attribute['value']['value']
                elif attribute['key'] == 'TARGETED_MONTHLY_SEARCHES':
                    if 'value' in attribute['value']:
                        for v in attribute['value']['value']:
                            if len(v) > 2:
                                entry[str(v[0]) + "-" + str(v[1])] = v[2]
                            else:
                                entry[str(v[0]) + "-" + str(v[1])] = 0
                elif attribute['key'] == 'COMPETITION':
                    if 'value' in attribute['value']:
                        entry['competition'] = attribute['value']['value']
                    else:
                        entry['competition'] = 0
                elif attribute['key'] == 'AVERAGE_CPC':
                    if 'value' in attribute['value']:
                        entry['cpc'] = int(attribute['value']['value']['microAmount']) / 1000000.0
                    else:
                        entry['cpc'] = 0
                elif attribute['key'] == 'CATEGORY_PRODUCTS_AND_SERVICES':
                    if 'value' in attribute['value']:
                        cats = []
                        for value in attribute['value']['value']:
                            try:
                                cats.append(TAX[value])
                            except KeyError:
                                pass
                        if len(cats) > 0:
                            # detect main category
                            for t in TAX_ORDER:
                                if t in cats:
                                    entry['cat'] = t
                                    break
            entries.append(entry)
    return entries


def read_file(filename, tokenize=False, shingles=0):
    with codecs.open(filename, 'r', 'utf-8') as f:
        lines = [x.strip('\n').strip(" ") for x in f.readlines()]

    if tokenize:
        newlines = []
        for line in lines:
            tmp = line
            while " " in tmp:
                tmp = line[0:tmp.rfind(" ")]
                newlines.append(tmp)
        lines = lines + newlines

    if shingles > 0:
        shingled_text = []
        for line in lines:
            vectorizer = CountVectorizer(ngram_range=(shingles, len(line)))
            analyzer = vectorizer.build_analyzer()
            shingled_text += analyzer(line)
        lines = shingled_text

    unique = set(lines)
    return list(unique)


TAX = dict()
TAX_ORDER = [
    'Vehicles', 'Computers & Consumer Electronics', 'Internet & Telecom',
    'Apparel', 'Sports & Fitness', 'Beauty & Personal Care', 'Health',
    'Business & Industrial', 'Food & Groceries', 'Home & Garden',
    'Family & Community', 'Arts & Entertainment', 'Hobbies & Leisure',
    'Occasions & Gifts', 'Finance', 'Travel & Tourism',
    'Retailers & General Merchandise', 'Real Estate', 'Jobs & Education',
    'Dining & Nightlife', 'Law & Government', 'News']


def read_taxonomy():
    taxonomy_file = os.path.join(os.path.dirname(__file__), os.pardir, 'keyword-planner', 'productsservices.csv')
    for line in open(taxonomy_file):
        l = line.split(",")
        try:
            TAX[int(l[0].strip('"'))] = (l[1].strip("\n").strip('"') + "/").split("/")[1]
        except ValueError:
            pass


def main(argv):
    args = argparser.parse_args()

    print >> sys.stderr, '# Start: Adwords Data: %s, %s' % (args.cc, datetime.datetime.now().time().isoformat())

    read_taxonomy()
    service = initialize_service()
    keywords = read_file(args.file, args.tokenize, args.shingles)

    bar = Bar('Processing', max=len(keywords), suffix='%(percent).1f%% - %(eta)ds')

    data = []
    if args.stats:
        # pagination of 800 items
        kws = keywords
        while len(kws) > 0:
            page = kws[0:PAGE_SIZE]
            kws = kws[PAGE_SIZE:]

            data = data + parse(args.cc, query_adwords(service, args.cc.split(","), page, "STATS"))

            bar.next(len(page))

    elif args.ideas:
        # pagination of 1 item
        for kw in keywords:
            data = data + parse(args.cc, query_adwords(service, args.cc.split(","), kw, "IDEAS"))

            bar.next()

    bar.finish()

    headers = sorted(data[0].keys(), reverse=True) if len(data) > 0 else [
        'keyword',
        'cpc',
        'competition',
        'cc',
        'cat',
        'search_volume',
        'year',
        'month',
        'product'
    ]
    output = pandas.DataFrame(data, columns=headers)
    if len(data) > 0:
        output = transpose_columns(output, product_name(args.file))
    output.to_csv(sys.stdout, header=True, index=False, encoding='utf-8-sig')

    print >> sys.stderr, '# End: Adwords Data: %s, %s' % (args.cc, datetime.datetime.now().time().isoformat())


def transpose_columns(df, product):
    id_vars = ['keyword', 'cpc', 'competition', 'cc', 'cat']

    if df.columns[4] != 'cat':
        del id_vars[4]

    df = df.melt(id_vars)
    df['year'], df['month'] = df['variable'].str.split('-', 1).str
    df.rename(columns={'value': 'search_volume'}, inplace=True)
    df.drop('variable', axis=1, inplace=True)
    df['product'] = product

    return df


def product_name(path):
    head = os.path.splitext(path)[0]
    return os.path.basename(head)


if __name__ == '__main__':
    main(sys.argv)
